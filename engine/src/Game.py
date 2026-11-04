from engine.src import MapGenerator, Bot
import json

class Game:
    def __init__(self, seed: int, map_generator: MapGenerator, bot1_path: str, bot2_path: str):
        self.seed = seed
        self.bot_paths = {1 : bot1_path, 2 : bot2_path}
        self.bots = {1 : Bot(bot1_path), 2 : Bot(bot2_path)}
        self.map = map_generator.generate_map(seed=seed)
    def start(self) -> dict:
        self.map = self.map_generator.generate_map(seed=self.seed)

    def init_message(self, player: int) -> str:
        return json.dumps({
            "type": "init",
            "version": "1.0",
            "player": player,
            "seed": self.seed,
            "size": len(self.map),
            "grid": self.map,                    # -1 / 0 / energie
            "bases": [
                {"player": 1, "x": self.bases[1][0], "y": self.bases[1][1]},
                {"player": 2, "x": self.bases[2][0], "y": self.bases[2][1]},
            ],
            "config": {
                "max_turns": 500,
                "move_budget": 1500,
                "start_energy": 1000,
                "ship_capacity": 100,
                "ship_cost": 500,
                "turn_timeout_ms": 1000,
            },
        })
    