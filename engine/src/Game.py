from engine.src import MapGenerator, Bot
import json
import Message

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



        

    def init_message(self, player: int) -> str:
        return Message.InitMessage(
            player=player,
            seed=self.seed,
            size=len(self.map),
            grid=self.map,
            config=Message.InitMessage.Config(
                max_turns=100,
                move_budget=10,
                start_energy=1000,
                ship_capacity=100,
                ship_cost=100,
                turn_timeout_ms=1000
            )
        ).to_json()
    