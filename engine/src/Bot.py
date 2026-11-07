import subprocess, sys, json, threading, queue, os

class BotError(Exception):
    pass

class Bot:
    def __init__(self, bot_path: str, player_id: int):
        if player_id not in [1, 2]:
            raise BotError(f"Invalid player ID: {player_id}")
        self.player_id = player_id
        cmd = self._prepare_cmd(bot_path)
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception as e:
            raise BotError(f"Failed to start bot process: {e}")

    def _prepare_cmd(self, bot_path: str) -> list[str]:
        if bot_path.endswith(".py"):
            return [sys.executable, bot_path]
        if bot_path.endswith(".cpp"):
            exec_name = os.path.splitext(bot_path)[0]
            result = subprocess.run(["g++", bot_path, "-o", exec_name], capture_output=True)
            if result.returncode != 0:
                raise BotError(f"Failed to compile C++ bot: {result.stderr}")
            return [os.path.abspath(exec_name)]
        raise BotError(f"Unsupported bot file type: {bot_path}")

    def send_message(self, msg: str) -> None:
        try:
            self.process.stdin.write(msg + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def receive_message(self, timeout_s: float = 1.0) -> dict | None:
        """Read one JSON line from the bot's stdout. Returns None on timeout or parse error."""
        buf: queue.Queue[str] = queue.Queue()

        def _read():
            buf.put(self.process.stdout.readline())

        t = threading.Thread(target=_read, daemon=True)
        t.start()
        t.join(timeout_s)

        if t.is_alive():
            return None  # timed out — caller decides what to do

        try:
            line = buf.get_nowait().strip()
        except queue.Empty:
            return None

        if not line:
            return None

        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None

    def terminate(self) -> None:
        try:
            self.process.stdin.close()
        except Exception:
            pass
        try:
            self.process.terminate()
        except Exception:
            pass
