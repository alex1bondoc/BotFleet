from engine.src import MapGenerator

class Game:
    def __init__(self, seed: int, map_generator: MapGenerator, bot1_path: str, bot2_path: str):
        self.seed = seed
        self.map_generator = map_generator
        self.bot_paths = {1 : bot1_path, 2 : bot2_path}
        self.bots = {1 : None, 2 : None}
        self.map = None
    def start(self) -> dict:
        self.map = self.map_generator.generate_map(seed=self.seed)
