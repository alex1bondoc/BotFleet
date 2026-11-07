import sys
import json
import time

init = json.loads(sys.stdin.readline())
pid = init["player"]

sys.stdout.write(json.dumps({"type": "ack", "player": pid}) + "\n")
sys.stdout.flush()

while True:
    line = sys.stdin.readline()
    if not line:
        break
    msg = json.loads(line)
    if msg["type"] == "done":
        break
    time.sleep(9999)
