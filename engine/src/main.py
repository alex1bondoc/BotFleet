import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from Game import Game
from Config import GameConfig

BOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "bots")

if __name__ == "__main__":
    bot_py  = os.path.join(BOTS_DIR, "bot.py")
    bot_cpp = os.path.join(BOTS_DIR, "bot.cpp")

    config = GameConfig()
    game = Game(seed=42, bot1_path=bot_py, bot2_path=bot_cpp, config=config)

    winner, reason = game.start()

    print(f"Game over — winner: Player {winner} ({reason})")
    print(f"Score  : P1={game.base_energy[1]}  P2={game.base_energy[2]}")
    print(f"Ships  : P1={len(game.ships[1])}  P2={len(game.ships[2])}")
    print(f"Budgets: P1={game.move_budget[1]}  P2={game.move_budget[2]}")
