import random

FREE = 0
OBSTACLE = -1

class MapGenerator:
    def __init__(
        self,
        size: int,
        obstacle_probability: int = 10,
        energy_probability: int = 6,
        deposit_energy: int = 100,
    ):
        self.size = size
        self.obstacle_probability = obstacle_probability
        self.energy_probability = energy_probability
        self.deposit_energy = deposit_energy
        self.energy_count = 0

    def generate_map(self, seed: int) -> list[list[int]]:
        rnd = random.Random(seed)
        map = [[FREE for _ in range(self.size)] for _ in range(self.size)]
        for y in range(self.size):
            for x in range(self.size // 2 + self.size % 2):
                r = rnd.randint(0, 99)
                if r < self.obstacle_probability:
                    map[y][x] = OBSTACLE
                elif r < self.obstacle_probability + self.energy_probability:
                    map[y][x] = self.deposit_energy
                    self.energy_count += 1
        map[0][0] = FREE
        for y in range(self.size):
            for x in range(self.size // 2 + self.size % 2, self.size):
                map[y][x] = map[self.size - 1 - y][self.size - 1 - x]

        if self.energy_count <= 0 or not self.is_valid_map(map): 
            return map
        else:
            return self.generate_map(seed + 1)

    def is_valid_map(self, map: list[list[int]]) -> bool:
        if not self.bfs(map, 0, 0) or not self.bfs(map, self.size - 1, self.size - 1):
            return False
        return True

    def bfs(self, map: list[list[int]], start_x: int, start_y: int) -> bool:
        visited = [[False for _ in range(self.size)] for _ in range(self.size)]
        queue = [(start_x, start_y)]
        visited[start_y][start_x] = True
        cnt = 0
        while queue:
            x, y = queue.pop(0)
            if map[y][x] == ENERGY:
                cnt += 1
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and not visited[ny][nx] and map[ny][nx] != OBSTACLE:
                    visited[ny][nx] = True
                    queue.append((nx, ny))
        return cnt == self.energy_count