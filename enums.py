from enum import Enum

class CellStates(Enum):
    empty = 1
    not_empty = 2

class StartModes(Enum):
    random_field = 1
    empty_field = 2
    full_field = 3
