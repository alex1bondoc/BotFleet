import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine", "src"))

import json
import logging
import traceback

import pika

from db import Database
from Game import Game
from Config import GameConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost/")
QUEUE_NAME   = os.environ.get("QUEUE_NAME",   "games")
HISTORY_DIR  = os.environ.get("HISTORY_DIR",  "/tmp/histories")
MAX_RETRIES  = int(os.environ.get("MAX_RETRIES", 3))

os.makedirs(HISTORY_DIR, exist_ok=True)


def run_game(job: dict) -> tuple[str, int | None]:
    config = GameConfig()
    game = Game(
        seed=job["seed"],
        bot1_path=job["bot1_path"],
        bot2_path=job["bot2_path"],
        config=config,
    )
    winner, reason = game.start()

    history = {
        "game_id":     job["game_id"],
        "seed":        job["seed"],
        "winner":      winner,
        "reason":      reason,
        "base_energy": game.base_energy,
        "move_budget": game.move_budget,
        "ships": {str(pid): ships for pid, ships in game.ships.items()},
    }

    path = os.path.join(HISTORY_DIR, f"{job['game_id']}.json")
    with open(path, "w") as f:
        json.dump(history, f)

    return path, winner


def on_message(ch, method, properties, body, db: Database) -> None:
    job         = json.loads(body)
    game_id     = job["game_id"]
    retry_count = job.get("retry_count", 0)

    log.info(f"[{game_id}] attempt {retry_count + 1}/{MAX_RETRIES + 1}")

    try:
        db.set_running(game_id)
        history_path, winner = run_game(job)
        db.set_done(game_id, history_path, winner)
        log.info(f"[{game_id}] done → {history_path}")

    except Exception:
        error_msg = traceback.format_exc()
        log.error(f"[{game_id}] failed (retry {retry_count}):\n{error_msg}")

        if retry_count < MAX_RETRIES:
            job["retry_count"] = retry_count + 1
            ch.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=json.dumps(job),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            log.info(f"[{game_id}] requeued (retry {retry_count + 1}/{MAX_RETRIES})")
        else:
            db.set_error(game_id, error_msg)
            log.error(f"[{game_id}] max retries reached, marked as error")

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    db = Database()

    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel    = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=lambda ch, m, p, body: on_message(ch, m, p, body, db),
    )

    log.info(f"Worker ready, consuming from '{QUEUE_NAME}'")
    channel.start_consuming()


if __name__ == "__main__":
    main()
