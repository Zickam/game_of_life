from enum import Enum

class CellStates(Enum):
    empty = 1
    not_empty = 2

class FieldStartModes(Enum):
    random_field = 1
    empty_field = 2
    full_field = 3

class GameStates(Enum):
    start_menu = 1
    playing = 2
