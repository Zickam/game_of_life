import builtins
import random
import time
from enum import Enum
import threading
import sys
import math
from collections.abc import Callable

import pygame as pg

import gui
from utils import Vector2
import enums

SAVE_FILE_PATH = "data/save.bin"
SAVE_FILE_PATTERN = bytearray([1, 1, 1, 0, 0, 1, 0, 0])


class Cell:
    def __init__(self, gui_object: gui.classes.Cell, state: enums.CellStates.__dict__ = enums.CellStates.empty, do_on_click_events: tuple[Callable, ...] = ()):
        self.__state = state
        self.__gui_object = gui_object
        self.do_on_click_events = do_on_click_events

        match self.__state:
            case enums.CellStates.not_empty:
                self.setActive()
            case enums.CellStates.empty:
                self.setInactive()
            case other:
                raise Exception(f"Unacceptable arg: {other}")

    def setDoOnClickEvents(self, do_on_click_events):
        self.do_on_click_events = do_on_click_events

    def changeState(self):
        match self.__state:
            case enums.CellStates.not_empty:
                self.setInactive()
            case enums.CellStates.empty:
                self.setActive()
            case other:
                raise Exception(f"Unexpected argument: {other}")

    def setInactive(self):
        self.__state = enums.CellStates.empty
        self.__gui_object.setInactive()

    def setActive(self):
        self.__state = enums.CellStates.not_empty
        self.__gui_object.setActive()

    def getState(self) -> enums.CellStates.__dict__:
        return self.__state

    def getGUIObject(self) -> gui.classes.Cell:
        return self.__gui_object

    def update(self, process_clicks: bool, mouse_click_state: tuple[int], mouse_pos: Vector2):
        gui_obj = self.__gui_object
        gui_obj.update()

        if process_clicks:
            is_mouse_pressed = mouse_click_state[0]
            is_mouse_inside = gui_obj.checkMouseWithinBounds(mouse_pos)

            if is_mouse_inside and is_mouse_pressed:
                if gui_obj.next_time_mouse_click_accepted <= time.time():
                    gui_obj.next_time_mouse_click_accepted = time.time() + gui_obj.MOUSE_CLICK_ACCEPT_TIME_INTERVAL
                    self.changeState()

    def doOnClick(self):
        for do_on_click_events in self.do_on_click_events:
            do_on_click_events()


class Field:
    def __init__(self,
                 gui_drawer: gui.classes.GUI_Drawer,
                 start_mode: enums.FieldStartModes.__dict__,
                 not_empty_cells_percent_approx: int,
                 grid_size: Vector2,
                 grid_thickness: int,
                 cell_size: Vector2,
                 cell_margin: Vector2, ):

        self.__gui_drawer = gui_drawer
        self.__start_mode = start_mode
        self.__not_empty_cells_percent_approx = not_empty_cells_percent_approx
        self.__grid_size = grid_size
        self.__cell_size = cell_size
        self.__cell_margin = cell_margin
        self.__grid_thickness = grid_thickness

        self.__field: list[list[Cell, ...], ...]
        self.initField()

    def initField(self):
        self.__field: list[list[Cell, ...], ...] = []

        cell_size_with_margin = self.__cell_size - self.__cell_margin
        cell_offset_margin_compensation = Vector2(self.__cell_margin.x // 2, self.__cell_margin.y // 2)

        for i in range(self.__grid_size.y):
            tmp = []
            for j in range(self.__grid_size.x):
                pos = Vector2(j * self.__cell_size.x + cell_offset_margin_compensation.x,
                              i * self.__cell_size.y + cell_offset_margin_compensation.y)
                gui_obj = gui.classes.Cell(self.__gui_drawer.screen,
                                           pos,
                                           cell_size_with_margin,
                                           gui.classes.Colors.black,
                                           gui.classes.Colors.purple
                                           )

                match self.__start_mode:
                    case enums.FieldStartModes.empty_field:
                        cell = Cell(gui_obj)
                    case enums.FieldStartModes.full_field:
                        cell = Cell(gui_obj)
                        cell.changeState()
                    case enums.FieldStartModes.random_field:
                        cell = self.randCellState(gui_obj, self.__not_empty_cells_percent_approx)

                tmp.append(cell)

            self.__field.append(tmp)

    def processTick(self) -> list[list[Cell, ...], ...]:
        new_field = []

        for i in range(len(self.__field)):
            tmp = []
            for j in range(len(self.__field[0])):
                cell = self.__field[i][j]

                neighbours = self.__getAmountOfNeighbours(i, j)
                new_cell = Cell(cell.getGUIObject(), cell.getState())

                if cell.getState() == enums.CellStates.not_empty:
                    if neighbours == 2 or neighbours == 3:
                        pass
                    else:
                        new_cell.changeState()

                if cell.getState() == enums.CellStates.empty:
                    if neighbours == 3:
                        new_cell.changeState()
                    else:
                        pass

                tmp.append(new_cell)

            new_field.append(tmp)

        self.__field = new_field

        return new_field

    def __getAmountOfNeighbours(self, i, j) -> int:
        amount_of_neighbours = 0

        if i > 0 and self.__field[i - 1][j].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1
        if i > 0 and j + 1 < len(self.__field[i]) and self.__field[i - 1][j + 1].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1
        if j + 1 < len(self.__field[i]) and self.__field[i][j + 1].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1
        if i + 1 < len(self.__field) and j + 1 < len(self.__field[i]) and self.__field[i + 1][j + 1].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1
        if i + 1 < len(self.__field) and self.__field[i + 1][j].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1
        if i + 1 < len(self.__field) and j > 0 and self.__field[i + 1][j - 1].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1
        if j > 0 and self.__field[i][j - 1].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1
        if i > 0 and j > 0 and self.__field[i - 1][j - 1].getState() == enums.CellStates.not_empty:
            amount_of_neighbours += 1

        return amount_of_neighbours

    @staticmethod
    def getRandomCellState(percent: int) -> enums.CellStates.__dict__:
        if not (0 <= percent <= 100):
            raise Exception("Not allowed percentage provided!")

        rand_num = random.randint(0, 100 - 1)

        if 0 <= rand_num <= percent:
            return enums.CellStates.not_empty
        else:
            return enums.CellStates.empty

    @classmethod
    def randCellState(cls, gui_obj: gui.classes.Cell, not_empty_cells_percent_approx: int) -> Cell:
        rand_cell_state = cls.getRandomCellState(not_empty_cells_percent_approx)

        match rand_cell_state:
            case enums.CellStates.empty:
                cell = Cell(gui_obj)

            case enums.CellStates.not_empty:
                cell = Cell(gui_obj)
                cell.changeState()

        return cell

    def getField(self) -> list[list[Cell, ...], ...]:
        return self.__field

    def saveField(self):
        with open(SAVE_FILE_PATH, "wb") as file:
            file.write(SAVE_FILE_PATTERN)
            array = []
            for i in range(len(self.__field)):
                for j in range(len(self.__field[i])):
                    match self.__field[i][j].getState():
                        case enums.CellStates.empty:
                            array.append(0)
                        case enums.CellStates.not_empty:
                            array.append(1)
                array.append(255)

            file.write(bytearray(array))

    def loadField(self):
        for i in range(len(self.__field)):
            for j in range(len(self.__field[i])):
                self.__field[i][j].setInactive()

        with open(SAVE_FILE_PATH, "rb") as file:
            start_pattern = file.read()[:len(SAVE_FILE_PATTERN)]
            if start_pattern != SAVE_FILE_PATTERN:
                raise Exception("Incorrect save file!")
            file.seek(len(SAVE_FILE_PATTERN))

            i, j = 0, 0
            for byte in file.read():
                if len(self.__field) < i:
                    continue
                if len(self.__field[i]) < j:
                    continue

                try:
                    match byte:
                        case 0:
                            self.__field[i][j].setInactive()
                            j += 1
                        case 1:
                            self.__field[i][j].setActive()
                            j += 1

                        case 255:
                            i += 1
                            j = 0

                except IndexError as ex:
                    raise Exception(f"Program can not load field that is bigger than active field yet or save file is corrupted: {ex}")

class GameObject:
    def __init__(self, gui_obj: gui.classes.GUI_Object, on_click_event: Callable):
        self.gui_obj = gui_obj
        self.on_click_event = on_click_event

    def onClick(self):
        self.on_click_event()


from enum import member

class Layout:
    class StartMenu(Enum):
        __start_btn_gui_obj = gui.classes.Cell()
        start_btn = GameObject("")
        settings_btn = GameObject("")

    class Game:
        @member
        class Grid(Enum):
            pass

        @member
        class Menu(Enum):
            pass

# print(Layout.StartMenu.__members__)
#
#
# exit()


class Game:
    GAME_STATE = enums.GameStates.start_menu

    MAX_FPS = 144
    GRID_SIZE = Vector2(35,  35)
    CELL_SIZE = Vector2(15,  15)
    CELL_MARGIN = Vector2(0, 0)
    # GRID_THICKNESS = round(0.08 * (CELL_SIZE.x + CELL_SIZE.y) / 2)
    GRID_THICKNESS = 0
    FIELD_START_MODE = enums.FieldStartModes.random_field
    NOT_EMPTY_CELLS_PERCENT_APPROX = 30
    MAX_GAME_ITERATIONS_PER_SECOND = 10
    PERFORM_ACTIONS_IN_PLACE = False
    CAP_FPS_TO_REAL_TIME_TICKS = False
    MENU_SIZE = Vector2(0, 200)
    GAME_ACTIVE = True
    GUI_ACTIVE = True
    MENU_LAYOUT = {
        "GameActive": {"obj": Cell, "state": enums.CellStates.not_empty, "gui_kwargs": {"pos": Vector2(0, 0), "size": Vector2(30, 30), "border_width": 4}},
        "GUIActive": {"obj": Cell, "state": enums.CellStates.not_empty,
                       "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(0, 31), "size": Vector2(30, 30), "border_width": 4}},
        "RefillField": {"obj": Cell, "state": enums.CellStates.empty,
                       "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(0, 62), "size": Vector2(30, 30), "border_width": 4}},
        "PlaceGlider": {"obj": Cell, "state": enums.CellStates.empty,
                        "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(0, 93), "size": Vector2(30, 30),
                                       "border_width": 4}},
        "PlaceMirrorer": {"obj": Cell, "state": enums.CellStates.empty,
                     "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(0, 124), "size": Vector2(30, 30),
                                    "border_width": 4}},

        "Increase max game speed": {"obj": Cell, "state": enums.CellStates.empty,
                        "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(150, 0), "size": Vector2(30, 30),
                                       "border_width": 4}},
        "Decrease max game speed": {"obj": Cell, "state": enums.CellStates.empty,
                                    "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(150, 31), "size": Vector2(30, 30),
                                                   "border_width": 4}},
        "Save field": {"obj": Cell, "state": enums.CellStates.empty,
                                    "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(350, 0), "size": Vector2(30, 30),
                                                   "border_width": 4}},
        "Load field": {"obj": Cell, "state": enums.CellStates.empty,
                                    "gui_kwargs": {"pos": Vector2(0, 0) + Vector2(350, 31), "size": Vector2(30, 30),
                                                   "border_width": 4}},
    }


    def __init__(self):
        self.max_fps = self.MAX_FPS

        self.not_empty_cells_percent_approx = self.NOT_EMPTY_CELLS_PERCENT_APPROX
        self.max_iterations_per_second = self.MAX_GAME_ITERATIONS_PER_SECOND
        self.perform_actions_in_place = self.PERFORM_ACTIONS_IN_PLACE
        self.field_start_mode = self.FIELD_START_MODE

        self.gui_drawer = gui.classes.GUI_Drawer(self.GRID_SIZE, self.GRID_THICKNESS, self.CELL_SIZE, self.MENU_SIZE, self.MENU_LAYOUT, self.MAX_FPS)
        self.field = Field(self.gui_drawer,
                           self.field_start_mode,
                           self.not_empty_cells_percent_approx,
                           self.GRID_SIZE,
                           self.GRID_THICKNESS,
                           self.CELL_SIZE,
                           self.CELL_MARGIN)

        self.max_iterations_per_second = self.MAX_GAME_ITERATIONS_PER_SECOND
        self.perform_iterations_on_original_field = self.PERFORM_ACTIONS_IN_PLACE
        self.calcNextIterationTime()

        self.shutdown = False
        self.game_active = self.GAME_ACTIVE
        self.gui_active = self.GUI_ACTIVE

        self.__frames_passed = 0
        self.__next_fps_update_time = time.time() + 1
        self._fps = self.__frames_passed / self.__next_fps_update_time

        self.__ticks_passed = 0
        self.__next_ticks_update_time = time.time() + 1
        self._ticks_per_second = round(self.__ticks_passed / self.__next_ticks_update_time)

        self.processEvents()


    def calcIterationsPerSecond(self):
        curr_time = time.time()
        if self.__next_ticks_update_time <= curr_time:
            self._ticks_per_second = self.__ticks_passed
            self.__ticks_passed = 0
            self.__next_ticks_update_time = time.time() + 1
            return self._ticks_per_second

    def calcFPS(self) -> int:
        curr_time = time.time()
        if self.__next_fps_update_time <= curr_time:
            self._fps = self.__frames_passed
            self.__frames_passed = 0
            self.__next_fps_update_time = time.time() + 1
            return self._fps

    def calcNextIterationTime(self):
        if self.max_iterations_per_second == 0:
            self.iterations_interval = math.inf
        else:
            self.iterations_interval: float = 1 / self.max_iterations_per_second
        self.next_iteration_time = time.time() + self.iterations_interval


    def processEvents(self):
        self.pg_events = pg.event.get()

        for event in self.pg_events:
            if event.type == pg.QUIT:
                self.shutdown = True

            if event.type == pg.KEYDOWN:
                if event.key == 32:
                    self.game_active = not self.game_active
                if event.key == 103: # 'g'
                    self.gui_active = not self.gui_active

    def processIteration(self):
        self.calcIterationsPerSecond()
        if self.game_active:
            if self.perform_iterations_on_original_field:
                processGameIterationInPlace(self.field)
            else:
                self.field.processTick()
            self.__ticks_passed += 1

    def runGame(self):
        while not self.shutdown:
            self.processEvents()

            if self.next_iteration_time <= time.time():
                self.processIteration()
                self.calcNextIterationTime()

    def processGUICells(self, mouse_click_state, mouse_pos):
        for line in self.field.getField():
            for cell in line:
                cell.update(not self.game_active, mouse_click_state, mouse_pos)

    def processGUIMenu(self, mouse_click_state, mouse_pos):
        for menu_btn, menu_text in zip(self.gui_drawer.menu.buttons, self.gui_drawer.menu.texts):
            menu_btn.update(True, mouse_click_state, mouse_pos)
            self.gui_drawer.renderCurrentStateText(menu_text, menu_btn.getGUIObject().pos + Vector2(menu_btn.getGUIObject().size.x, 0))

            match menu_text:
                case "GameActive":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            self.game_active = True
                        case enums.CellStates.empty:
                            self.game_active = False
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "GUIActive":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            self.gui_active = True
                        case enums.CellStates.empty:
                            self.gui_active = False
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "RefillField":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            self.field.is_initializing = True
                            self.field.initField()
                            self.field.is_initializing = True
                            menu_btn.changeState()

                        case enums.CellStates.empty:
                            pass
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "Increase max game speed":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            self.max_iterations_per_second += 1
                            menu_btn.changeState()

                        case enums.CellStates.empty:
                            pass
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "Decrease max game speed":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            if self.max_iterations_per_second > 1:
                                self.max_iterations_per_second -= 1
                            menu_btn.changeState()

                        case enums.CellStates.empty:
                            pass
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "Save field":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            self.field.saveField()
                            menu_btn.changeState()

                        case enums.CellStates.empty:
                            pass
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "Load field":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            self.field.loadField()
                            menu_btn.changeState()

                        case enums.CellStates.empty:
                            pass
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "PlaceGlider":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            raise NotImplementedError
                            menu_btn.changeState()

                        case enums.CellStates.empty:
                            pass
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")

                case "PlaceMirrorer":
                    state = menu_btn.getState()
                    match state:
                        case enums.CellStates.not_empty:
                            raise NotImplementedError
                            menu_btn.changeState()

                        case enums.CellStates.empty:
                            pass
                        case other:
                            raise Exception(f"Unacceptable argument: {other}")


    def processGUI(self):

        self.gui_drawer.clearScreen()

        mouse_pos = pg.mouse.get_pos()
        mouse_pos = Vector2(mouse_pos[0], mouse_pos[1])
        mouse_click_state = pg.mouse.get_pressed()

        self.processGUIMenu(mouse_click_state, mouse_pos)

        if self.gui_active:
            self.processGUICells(mouse_click_state, mouse_pos)

            self.gui_drawer.drawGrid()
            self.gui_drawer.drawMenu()

        text_pos = Vector2(0, self.gui_drawer.screen_size.y - self.gui_drawer.pg_font.get_height())
        self.gui_drawer.renderCurrentStateText('You can draw whatever you want if you stop the game processing',
                                               text_pos)

        text_pos = Vector2(self.gui_drawer.screen_size.x - 80, self.gui_drawer.screen_size.y - self.gui_drawer.pg_font.get_height())
        self.gui_drawer.renderCurrentStateText(f"fps: {self._fps}", text_pos)
        text_pos = Vector2(self.gui_drawer.screen_size.x - 191,
                           self.gui_drawer.screen_size.y - self.gui_drawer.pg_font.get_height() * 2)
        self.gui_drawer.renderCurrentStateText(f"iterations_per_second: {self._ticks_per_second}", text_pos)

        text_pos = Vector2(self.gui_drawer.screen_size.x - 210,
                           self.gui_drawer.screen_size.y - self.gui_drawer.pg_font.get_height() * 3)
        self.gui_drawer.renderCurrentStateText(f"Max iterations_per_second: {self.max_iterations_per_second}", text_pos)

        self.__frames_passed += 1
        self.calcFPS()

    def capFPS(self):
        if not self.game_active or self._ticks_per_second < 5:
            self.gui_drawer.setMaxFPS(self.max_fps)
        elif self.CAP_FPS_TO_REAL_TIME_TICKS and self._ticks_per_second > 1:
            self.gui_drawer.setMaxFPS(self._ticks_per_second + 1)

    def runGUI(self):
        while not self.shutdown:
            self.processGUI()

            self.capFPS()

            self.gui_drawer.updateScreen()

    def runGUI_threaded(self):
        self.gui_thread = threading.Thread(target=self.runGUI, args=())
        self.gui_thread.start()

    def runStartMenu(self):
        while 1:
            self.gui_drawer.drawStartMenu()

        self.runGUI_threaded()
        self.runGame()

def processGameIterationInPlace(_field: list[list[Cell, ...], ...]):
    """
    Doesnt work properly due to per-line processing
    """
    raise NotImplementedError
    for i in range(len(_field)):
        for j in range(len(_field[0])):
            cell = _field[i][j]
            neighbours = getAmountOfNeighbours(_field, i, j)

            if cell.state == classes.CellStates.not_empty:
                if neighbours == 2 or neighbours == 3:
                    pass
                else:
                    cell.state = classes.CellStates.empty
                    cell.gui_object.color = gui.classes.Colors.black

            if cell.state == classes.CellStates.empty:
                if neighbours == 3:
                    cell.state = classes.CellStates.not_empty
                    cell.gui_object.color = gui.classes.Colors.purple
                else:
                    pass

def calcScreenSize(grid_size: Vector2, cell_size: Vector2) -> Vector2:
    return Vector2(grid_size.x * cell_size.x, grid_size.y * cell_size.y)


def main():
    game = Game()

    game.runStartMenu()

main()