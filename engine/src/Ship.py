class Ship:
    def __init__(self, capacity: int, x: int, y: int):
        self.capacity = capacity
        self.x = x
        self.y = y
        self.energy = 0
        self.directions = { NORTH: (0, -1), SOUTH: (0, 1), WEST: (-1, 0), EAST: (1, 0) }

    def move(self, direction: str):
        if direction not in self.directions:
            raise ValueError(f"Invalid direction: {direction}")
        dx, dy = self.directions[direction]
        self.x += dx
        self.y += dy