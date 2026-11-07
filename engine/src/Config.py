import os

class GameConfig:
    """
    Single source of truth for all engine parameters.
    Every field can be overridden via the matching environment variable.
    """

    def __init__(self):
        # Map generation
        self.map_size             = int(os.environ.get("MAP_SIZE",                   16))
        self.obstacle_probability = int(os.environ.get("OBSTACLE_PROBABILITY",       10))
        self.energy_probability   = int(os.environ.get("ENERGY_PROBABILITY",          6))
        self.deposit_energy       = int(os.environ.get("DEPOSIT_ENERGY",            100))

        # Game rules
        self.max_turns            = int(os.environ.get("MAX_TURNS",                 500))
        self.move_budget          = int(os.environ.get("MOVE_BUDGET",              1000))
        self.start_energy         = int(os.environ.get("START_ENERGY",             1000))
        self.ship_capacity        = int(os.environ.get("SHIP_CAPACITY",             100))
        self.ship_cost            = int(os.environ.get("SHIP_COST",                 500))

        # Timing & bot management
        self.turn_timeout_ms          = int(os.environ.get("TURN_TIMEOUT_MS",          1000))
        self.init_timeout_ms          = int(os.environ.get("INIT_TIMEOUT_MS",          5000))
        self.max_consecutive_timeouts = int(os.environ.get("MAX_CONSECUTIVE_TIMEOUTS",    3))
