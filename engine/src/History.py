from dataclasses import asdict, dataclass
import json

@dataclass
class History:
    map = list[list[int]]
    map_size: int
    winner = int | None
    reason: str
    turns: list['Turn']

    def to_json(self) -> str:
        return json.dumps(**asdict(self))

@dataclass
class Turn:
    ships = list[dict]
    score = dict[int, int]