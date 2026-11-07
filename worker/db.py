import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/botfleet")

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True

    def set_running(self, game_id: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE games SET status = 'running', updated_at = NOW() WHERE id = %s",
                (game_id,),
            )

    def set_done(self, game_id: str, history_path: str, winner: int | None) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE games SET status = 'done', history_path = %s, winner = %s, updated_at = NOW() WHERE id = %s",
                (history_path, winner, game_id),
            )

    def set_error(self, game_id: str, error: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE games SET status = 'error', error = %s, updated_at = NOW() WHERE id = %s",
                (error, game_id),
            )
