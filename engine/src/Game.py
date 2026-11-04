from engine.src import MapGenerator, Bot
import json

class Game:
    def __init__(self, seed: int, map_generator: MapGenerator, bot1_path: str, bot2_path: str):
        self.seed = seed
        self.bots = {1 : Bot(bot1_path, 1), 2 : Bot(bot2_path, 2)}
        self.map = map_generator.generate_map(seed=seed)
    def start(self) -> dict:
        for player_id, bot in self.bots.items():
            init_msg = self.init_message(player_id)
            bot.send_message(init_msg)
            response = bot.receive_message()
            if response.get("type") != "ack":
                raise ValueError(f"Bot {player_id} did not acknowledge init message: {response}")
        return {"status": "ok", "message": "Game started successfully."}

    def init_message(self, player: int) -> str:
        return json.dumps({
            "type": "init",
            "version": "1.0",
            "player": player,
            "seed": self.seed,
            "size": len(self.map),
            "grid": self.map,
            "config": {
                "max_turns": 500,
                "move_budget": 1500,
                "start_energy": 1000,
                "ship_capacity": 100,
                "ship_cost": 500,
                "turn_timeout_ms": 1000,
            },
        })
    