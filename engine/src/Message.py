import json
from dataclasses import dataclass, field, asdict

@dataclass
class Message:
    TYPE = "Message"
    def to_json(self) -> str:
        return json.dumps({"type": self.TYPE, **asdict(self)})

@dataclass
class InitMessage(Message):
    TYPE = "init"

    @dataclass(frozen=True)
    class Config:
        max_turns: int
        move_budget: int
        start_energy: int
        ship_capacity: int
        ship_cost: int
        turn_timeout_ms: int

    player: int
    seed: int
    size: int
    grid: list[list[int]]
    config: Config

@dataclass
class AckMessage(Message):
    TYPE = "ack"
    player: int

@dataclass
class CommandMessage(Message):
    TYPE = "command"
    player: int
    commands: list[str]
    build: bool = False

@dataclass
class UpdateMessage(Message):
    TYPE = "update"
    player: int
    turn: int
    energy: int
    ships: list[dict] = field(default_factory=list)
    deposits_changed: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)

@dataclass
class DoneMessage(Message):
    TYPE = "done"
    winner: int | None
    reason: str
