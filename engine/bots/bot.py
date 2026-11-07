import sys
import json

def direction_towards(sx, sy, tx, ty):
    dx, dy = tx - sx, ty - sy
    if abs(dx) >= abs(dy):
        return "EAST" if dx > 0 else "WEST"
    return "SOUTH" if dy > 0 else "NORTH"

def nearest(sx, sy, targets):
    return min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy), default=None)

def main():
    init = json.loads(sys.stdin.readline())
    pid = init["player"]
    size = init["size"]
    grid = init["grid"]
    ship_capacity = init["config"]["ship_capacity"]
    base = (0, 0) if pid == 1 else (size - 1, size - 1)

    sys.stdout.write(json.dumps({"type": "ack", "player": pid}) + "\n")
    sys.stdout.flush()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg["type"] == "done":
            break

        for ch in msg.get("deposits_changed", []):
            grid[ch["y"]][ch["x"]] = ch["energy"]

        deposits = [(x, y) for y in range(size) for x in range(size) if grid[y][x] > 0]
        my_ships = sorted([s for s in msg["ships"] if s["player"] == pid], key=lambda s: s["id"])

        cmds = []
        for ship in my_ships:
            sx, sy, cargo = ship["x"], ship["y"], ship["cargo"]

            if grid[sy][sx] > 0 and cargo < ship_capacity:
                cmds.append("STAY")
            elif cargo >= ship_capacity or not deposits:
                cmds.append(direction_towards(sx, sy, *base))
            else:
                target = nearest(sx, sy, deposits)
                cmds.append(direction_towards(sx, sy, *target))

        sys.stdout.write(json.dumps({"type": "command", "player": pid, "commands": cmds, "build": False}) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
