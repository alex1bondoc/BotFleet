import subprocess, sys, threading, queue

class BotError(Exception):
    pass

DONE = False

class Bot:
    def __init__(self, bot_path: str, player_id: int):
        cmd = self.prepare_bot(bot_path)
        try:
            self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            raise BotError(f"Failed to start bot process: {e}")
        self.map_size = None
        self.map = None
        self.timouts = 0
        self.ships = []
        self.energy = 1000
        self.turn = 0
        self.available_moves = None
        if player_id not in [1, 2]:
            raise BotError(f"Invalid player ID: {player_id}")
        if player_id == 1:
            self.base = (0, 0)
        else:
            self.base = (self.map_size - 1, self.map_size - 1)
        ships = [Ship(capacity=100, x=self.base[0], y=self.base[1])]
    def prepare_bot(self, bot_path: str) -> list[str]:
        if (bot_path.endswith(".py")):
            return [sys.executable, bot_path]
        elif (bot_path.endswith(".cpp")):
            exec_name = os.path.splitext(bot_path)[0]
            compile_cmd = ["g++", bot_path, "-o", exec_name]
            compile = subprocess.run(compile_cmd, check=True)
            if (compile.returncode != 0):
                raise BotError(f"Failed to compile C++ bot: {bot_path}")
            return [os.path.abspath(exec_name)]


        