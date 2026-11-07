NORTH = "NORTH"
SOUTH = "SOUTH"
EAST  = "EAST"
WEST  = "WEST"
STAY  = "STAY"

DIRECTIONS = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST:  (1, 0),
    WEST:  (-1, 0),
}

class Ship:
    def __init__(self, capacity: int, x: int, y: int):
        self.capacity = capacity
        self.x = x
        self.y = y
        self.cargo = 0

    def move(self, direction: str) -> None:
        if direction not in DIRECTIONS:
            raise ValueError(f"Invalid direction: {direction}")
        dx, dy = DIRECTIONS[direction]
        self.x += dx
        self.y += dy
