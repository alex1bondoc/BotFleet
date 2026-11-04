import subprocess, sys, threading, queue

class BotError(Exception):
    pass

DONE = False

class Bot:
    def __init__(self, bot_path: str):
        cmd = self.prepare_bot(bot_path)
        try:
            self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            raise BotError(f"Failed to start bot process: {e}")
        self.map_size = None
        self.map = None
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

    def run(self) -> None:
        get_map()
        while not DONE:
            


    def get_map(self) -> None:
        self.map_size = int(self.process.stdout.readline().strip())
        self.map = [[0 for _ in range(self.map_size)] for _ in range(self.map_size)]
        for i in range(self.map_size):
            for j in range(self.map_size):
                self.map[i][j] = int(self.process.stdout.readline().strip())

        