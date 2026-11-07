import copy
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from MapGenerator import MapGenerator
from Bot import Bot, BotError
from Config import GameConfig
import Message

OBSTACLE = -1

DIRECTIONS = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST":  (1, 0),
    "WEST":  (-1, 0),
}


class Game:
    def __init__(self, seed: int, bot1_path: str, bot2_path: str, config: GameConfig | None = None):
        self.seed = seed
        self.config = config or GameConfig()
        self.size = self.config.map_size

        gen = MapGenerator(
            size=self.config.map_size,
            obstacle_probability=self.config.obstacle_probability,
            energy_probability=self.config.energy_probability,
            deposit_energy=self.config.deposit_energy,
        )
        self.static_grid = gen.generate_map(seed=seed)
        self.grid = copy.deepcopy(self.static_grid)

        self.bots = {
            1: Bot(bot1_path, 1),
            2: Bot(bot2_path, 2),
        }

        self._consecutive_timeouts = {1: 0, 2: 0}
        self._eliminated = {1: False, 2: False}
        self._elimination_turn: dict[int, int | None] = {1: None, 2: None}

        self.base_energy = {1: self.config.start_energy, 2: self.config.start_energy}
        self.move_budget = {1: self.config.move_budget, 2: self.config.move_budget}
        self._next_ship_id = 0

        self.ships: dict[int, list[dict]] = {
            1: [self._new_ship(1, 0, 0)],
            2: [self._new_ship(2, self.size - 1, self.size - 1)],
        }

    # --- helpers ---

    def _new_ship(self, player: int, x: int, y: int) -> dict:
        s = {"id": self._next_ship_id, "player": player, "x": x, "y": y, "cargo": 0}
        self._next_ship_id += 1
        return s

    def _base_pos(self, player: int) -> tuple[int, int]:
        return (0, 0) if player == 1 else (self.size - 1, self.size - 1)

    def _all_ships(self) -> list[dict]:
        return self.ships[1] + self.ships[2]

    # --- message builders ---

    def _protocol_config(self) -> Message.InitMessage.Config:
        return Message.InitMessage.Config(
            max_turns=self.config.max_turns,
            move_budget=self.config.move_budget,
            start_energy=self.config.start_energy,
            ship_capacity=self.config.ship_capacity,
            ship_cost=self.config.ship_cost,
            turn_timeout_ms=self.config.turn_timeout_ms,
        )

    def _init_message(self, player: int) -> str:
        return Message.InitMessage(
            player=player,
            seed=self.seed,
            size=self.size,
            grid=self.static_grid,
            config=self._protocol_config(),
        ).to_json()

    def _update_message(self, player: int, turn: int, deposits_changed: list[dict]) -> str:
        ships_sorted = sorted(self._all_ships(), key=lambda s: s["id"])
        return Message.UpdateMessage(
            player=player,
            turn=turn,
            energy=self.base_energy[player],
            ships=ships_sorted,
            deposits_changed=deposits_changed,
        ).to_json()

    # --- main entry point ---

    def start(self) -> tuple[int | None, str]:
        # Handshake: send init, expect ack
        for pid, bot in self.bots.items():
            bot.send_message(self._init_message(pid))
            resp = bot.receive_message(timeout_s=self.config.init_timeout_ms / 1000.0)
            if resp is None or resp.get("type") != "ack":
                raise BotError(f"Bot {pid} failed init handshake: {resp}")

        # Game loop
        pending_deposits: list[dict] = []

        for turn in range(self.config.max_turns):
            if self._is_over():
                break

            # Send current state to each active bot
            for pid, bot in self.bots.items():
                if self._eliminated[pid]:
                    continue
                bot.send_message(self._update_message(pid, turn, pending_deposits))

            # Collect commands from each bot
            timeout_s = self.config.turn_timeout_ms / 1000.0
            commands: dict[int, dict | None] = {}
            for pid, bot in self.bots.items():
                if self._eliminated[pid]:
                    commands[pid] = None
                    continue
                resp = bot.receive_message(timeout_s=timeout_s)
                if resp is None:
                    self._consecutive_timeouts[pid] += 1
                    if self._consecutive_timeouts[pid] >= self.config.max_consecutive_timeouts:
                        self._eliminated[pid] = True
                        self._elimination_turn[pid] = turn
                    commands[pid] = None
                else:
                    self._consecutive_timeouts[pid] = 0
                    commands[pid] = resp

            # Advance game state
            pending_deposits = self._process_turn(commands, turn)

        winner, reason = self._determine_winner()

        # Notify bots the game is done
        done_msg = Message.DoneMessage(winner=winner, reason=reason).to_json()
        for bot in self.bots.values():
            bot.send_message(done_msg)
            bot.terminate()

        return winner, reason

    # --- game logic ---

    def _is_over(self) -> bool:
        if self._eliminated[1] and self._eliminated[2]:
            return True
        if any(self.move_budget[p] > 0 for p in [1, 2]):
            return False
        for pid in [1, 2]:
            for ship in self.ships[pid]:
                if self.grid[ship["y"]][ship["x"]] > 0:
                    return False
        return True

    def _process_turn(self, commands: dict[int, dict | None], turn: int) -> list[dict]:
        # 1. Build new ships (command processed this turn, ship available next tick)
        self._pending_builds: dict[int, bool] = {}
        for pid in [1, 2]:
            cmd = commands.get(pid)
            if cmd and cmd.get("build") and self.base_energy[pid] >= self.config.ship_cost:
                bx, by = self._base_pos(pid)
                base_free = all(s["x"] != bx or s["y"] != by for s in self.ships[pid])
                if base_free:
                    self.base_energy[pid] -= self.config.ship_cost
                    self.ships[pid].append(self._new_ship(pid, bx, by))

        # 2. Compute new positions (simultaneous movement)
        old_pos: dict[int, tuple[int, int]] = {
            s["id"]: (s["x"], s["y"])
            for s in self._all_ships()
        }
        new_pos: dict[int, tuple[int, int]] = {}

        for pid in [1, 2]:
            cmd = commands.get(pid)
            ship_cmds: list[str] = cmd.get("commands", []) if cmd else []
            enemy = 3 - pid
            ex, ey = self._base_pos(enemy)
            player_ships = sorted(self.ships[pid], key=lambda s: s["id"])

            for i, ship in enumerate(player_ships):
                action = ship_cmds[i].upper() if i < len(ship_cmds) else "STAY"
                ox, oy = old_pos[ship["id"]]

                if action not in DIRECTIONS or self.move_budget[pid] <= 0:
                    new_pos[ship["id"]] = (ox, oy)
                    continue

                dx, dy = DIRECTIONS[action]
                nx, ny = ox + dx, oy + dy

                if not (0 <= nx < self.size and 0 <= ny < self.size):
                    new_pos[ship["id"]] = (ox, oy)
                    continue
                if self.static_grid[ny][nx] == OBSTACLE:
                    new_pos[ship["id"]] = (ox, oy)
                    continue
                if (nx, ny) == (ex, ey):
                    new_pos[ship["id"]] = (ox, oy)
                    continue

                new_pos[ship["id"]] = (nx, ny)
                self.move_budget[pid] -= 1

        # Apply moves
        for s in self._all_ships():
            s["x"], s["y"] = new_pos[s["id"]]

        # 3. Resolve collisions
        from collections import defaultdict
        pos_to_ships: dict[tuple, list[tuple[int, dict]]] = defaultdict(list)
        for pid in [1, 2]:
            for ship in self.ships[pid]:
                pos_to_ships[(ship["x"], ship["y"])].append((pid, ship))

        to_destroy: set[int] = set()
        for (cx, cy), occupants in pos_to_ships.items():
            if len(occupants) <= 1:
                continue
            # Ships on their own base are safe
            safe_ids: set[int] = set()
            for pid in [1, 2]:
                bx, by = self._base_pos(pid)
                if (cx, cy) == (bx, by):
                    safe_ids.update(s["id"] for p, s in occupants if p == pid)
            for pid, ship in occupants:
                if ship["id"] not in safe_ids:
                    self.grid[cy][cx] += ship["cargo"]
                    to_destroy.add(ship["id"])

        for pid in [1, 2]:
            self.ships[pid] = [s for s in self.ships[pid] if s["id"] not in to_destroy]

        # 4. Collection (ships that did not move, on a deposit)
        deposit_changes: dict[tuple[int, int], int] = {}
        for pid in [1, 2]:
            for ship in self.ships[pid]:
                sid = ship["id"]
                if new_pos.get(sid) != old_pos.get(sid):
                    continue  # ship moved
                cx, cy = ship["x"], ship["y"]
                cell = self.grid[cy][cx]
                if cell <= 0:
                    continue
                collect = min(-(-cell // 10), self.config.ship_capacity - ship["cargo"])  # ceil(cell/10)
                if collect <= 0:
                    continue
                ship["cargo"] += collect
                self.grid[cy][cx] -= collect
                deposit_changes[(cx, cy)] = self.grid[cy][cx]

        # 5. Deposit cargo at base
        for pid in [1, 2]:
            bx, by = self._base_pos(pid)
            for ship in self.ships[pid]:
                if ship["x"] == bx and ship["y"] == by and ship["cargo"] > 0:
                    self.base_energy[pid] += ship["cargo"]
                    ship["cargo"] = 0

        return [{"x": x, "y": y, "energy": e} for (x, y), e in deposit_changes.items()]

    def _determine_winner(self) -> tuple[int | None, str]:
        e1, e2 = self.base_energy[1], self.base_energy[2]
        if e1 != e2:
            return (1 if e1 > e2 else 2), "score"
        n1, n2 = len(self.ships[1]), len(self.ships[2])
        if n1 != n2:
            return (1 if n1 > n2 else 2), "ships"
        c1 = sum(s["cargo"] for s in self.ships[1])
        c2 = sum(s["cargo"] for s in self.ships[2])
        if c1 != c2:
            return (1 if c1 > c2 else 2), "cargo"
        return None, "draw"
