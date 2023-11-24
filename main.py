import random
import time
from enum import Enum
import threading
import sys
import math

import pygame as pg

import gui
from utils import Vector2
import constants



class Cell:
    def __init__(self, state: constants.CellStates.__dict__, gui_object):
        self.state = state
        self.gui_object = gui_object


class Game:
    def __init__(self, gui_drawer: gui.classes.GUI_Drawer, field: list[list[Cell, ...], ...],
                 max_iterations_per_second: float, perform_iterations_on_original_field: bool = True):
        self.gui_drawer = gui_drawer
        self.field = field

        self.max_iterations_per_second = max_iterations_per_second
        self.perform_iterations_on_original_field = perform_iterations_on_original_field

        self.calcNextIterationTime()

        self.shutdown = False
        self.game_active = True
        self.gui_active = True

        self.frames_passed = 0
        self.next_fps_update_time = time.time() + 1
        self.fps = self.frames_passed / self.next_fps_update_time

        self.iterations_passed = 0
        self.next_iterations_update_time = time.time() + 1
        self.iterations_per_second = self.iterations_passed / self.next_iterations_update_time

        self.processEvents()

    def calcIterationsPerSecond(self):
        curr_time = time.time()
        if self.next_iterations_update_time <= curr_time:
            self.iterations_per_second = self.iterations_passed
            self.iterations_passed = 0
            self.next_iterations_update_time = time.time() + 1
            return self.iterations_per_second

    def calcFPS(self) -> int:
        curr_time = time.time()
        if self.next_fps_update_time <= curr_time:
            self.fps = self.frames_passed
            self.frames_passed = 0
            self.next_fps_update_time = time.time() + 1
            return self.fps

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
                exit()
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
                self.field = processGameIteration(self.field)
            self.iterations_passed += 1

    def runGame(self):
        while 1:
            self.processEvents()

            if self.next_iteration_time <= time.time():
                self.processIteration()
                self.calcNextIterationTime()

    def processGUI(self):
        if self.gui_active:
            self.gui_drawer.clearScreen()

            mouse_pos = pg.mouse.get_pos()
            mouse_pos = Vector2(mouse_pos[0], mouse_pos[1])
            mouse_click_state = pg.mouse.get_pressed()

            for line in self.field:
                for cell in line:
                    gui_obj = cell.gui_object
                    gui_obj.update()

                    is_pressed = mouse_click_state[0]
                    is_inside = gui_obj.checkMouseWithinBounds(mouse_pos)

                    if is_inside and is_pressed:
                        if gui_obj.next_time_mouse_click_accepted <= time.time():
                            gui_obj.next_time_mouse_click_accepted = time.time() + gui_obj.MOUSE_CLICK_ACCEPT_TIME_INTERVAL
                            gui_obj.swapColor()
                            if cell.state == constants.CellStates.not_empty:
                                cell.state = constants.CellStates.empty
                            elif cell.state == constants.CellStates.empty:
                                cell.state = constants.CellStates.not_empty

            self.gui_drawer.drawGrid()
            self.frames_passed += 1

            self.calcFPS()


        text_pos = Vector2(0, 0)
        self.gui_drawer.renderCurrentStateText('You can draw whatever you want if you stop the game processing',
                                               text_pos)

        text_pos += Vector2(0, self.gui_drawer.pg_font.get_height())
        if self.game_active:
            self.gui_drawer.renderCurrentStateText('Game is ongoing (press spacebar to stop)', text_pos)
        else:
            self.gui_drawer.renderCurrentStateText('Game stopped (press spacebar to start)', text_pos)

        text_pos += Vector2(0, self.gui_drawer.pg_font.get_height())
        if self.gui_active:
            self.gui_drawer.renderCurrentStateText('Gui is processing (press g to stop)', text_pos)
        else:
            self.gui_drawer.renderCurrentStateText('Gui is not processing (press g to start)', text_pos)


        text_pos = Vector2(0, self.gui_drawer.screen_size.y) - Vector2(0, self.gui_drawer.pg_font.get_height())
        self.gui_drawer.renderCurrentStateText(f"fps: {self.fps}", text_pos)
        text_pos = Vector2(0, self.gui_drawer.screen_size.y) - Vector2(0, self.gui_drawer.pg_font.get_height() * 2)
        self.gui_drawer.renderCurrentStateText(f"iterations_per_second: {self.iterations_per_second}", text_pos)
    def runGUI(self):
        while 1:
            if self.shutdown:
                exit()

            self.processGUI()

            self.gui_drawer.updateScreen()

    def runGUI_threaded(self):
        self.gui_thread = threading.Thread(target=self.runGUI, args=())
        self.gui_thread.start()

def getAmountOfNeighbours(field: list[list[Cell, ...], ...], i, j) -> int:
    amount_of_neighbours = 0

    if i > 0 and field[i - 1][j].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1
    if i > 0 and j + 1 < len(field[i]) and field[i - 1][j + 1].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1
    if j + 1 < len(field[i]) and field[i][j + 1].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1
    if i + 1 < len(field) and j + 1 < len(field[i]) and field[i + 1][j + 1].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1
    if i + 1 < len(field) and field[i + 1][j].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1
    if i + 1 < len(field) and j > 0 and field[i + 1][j - 1].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1
    if j > 0 and field[i][j - 1].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1
    if i > 0 and j > 0 and field[i - 1][j - 1].state == constants.CellStates.not_empty:
        amount_of_neighbours += 1

    return amount_of_neighbours


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


def processGameIteration(_field: list[list[Cell, ...], ...]) -> list[list[Cell, ...], ...]:
    new_field = []
    for i in range(len(_field)):
        tmp = []
        for j in range(len(_field[0])):
            cell = _field[i][j]
            old_gui_obj = cell.gui_object

            neighbours = getAmountOfNeighbours(_field, i, j)

            gui_object = gui.classes.Cell(old_gui_obj.screen,
                                          old_gui_obj.pos,
                                          old_gui_obj.size,
                                          old_gui_obj.inactive_color,
                                          old_gui_obj.active_color)

            if cell.state == constants.CellStates.not_empty:
                if neighbours == 2 or neighbours == 3:
                    new_cell = Cell(
                        constants.CellStates.not_empty,
                        gui_object
                    )
                    gui_object.swapColor()
                    tmp.append(new_cell)
                else:
                    new_cell = Cell(
                        constants.CellStates.empty,
                        gui_object
                    )
                    tmp.append(new_cell)

            if cell.state == constants.CellStates.empty:
                if neighbours == 3:
                    new_cell = Cell(
                        constants.CellStates.not_empty,
                        gui_object
                    )
                    gui_object.swapColor()
                    tmp.append(new_cell)
                else:

                    new_cell = Cell(
                        constants.CellStates.empty,
                        gui_object
                    )
                    tmp.append(new_cell)
        new_field.append(tmp)

    return new_field


def getRandomCellState(percent: int) -> constants.CellStates.__dict__:
    rand_num = random.randint(0, 100 - 1)

    if 0 <= rand_num <= percent:
        return constants.CellStates.not_empty
    else:
        return constants.CellStates.empty

def randCellState(gui_obj: gui.classes.Cell, not_empty_cells_percent_approx: int) -> Cell:
    rand_cell_state = getRandomCellState(not_empty_cells_percent_approx)

    match rand_cell_state:
        case constants.CellStates.empty:
            cell = Cell(constants.CellStates.empty, gui_obj)

        case constants.CellStates.not_empty:
            gui_obj.swapColor()
            cell = Cell(constants.CellStates.not_empty, gui_obj)

    return cell

def initField(screen: pg.display, grid_size: Vector2, cell_size: Vector2, cell_margin: Vector2, not_empty_cells_percent_approx: int, start_mode: constants.StartModes.__dict__) -> list[list[Cell, ...], ...]:
    field = []

    cell_size_with_margin = cell_size - cell_margin
    cell_offset_margin_compensation = Vector2(cell_margin.x // 2, cell_margin.y // 2)

    for i in range(grid_size.y):
        tmp = []
        for j in range(grid_size.x):
            pos = Vector2(j * cell_size.x + cell_offset_margin_compensation.x, i * cell_size.y + cell_offset_margin_compensation.y)
            gui_obj = gui.classes.Cell(screen,
                                       pos,
                                       cell_size_with_margin,
                                       gui.classes.Colors.black,
                                       gui.classes.Colors.purple
                                       )

            match start_mode:
                case constants.StartModes.empty_field:
                    cell = Cell(constants.CellStates.empty, gui_obj)
                case constants.StartModes.full_field:
                    gui_obj.swapColor()
                    cell = Cell(constants.CellStates.not_empty, gui_obj)
                case constants.StartModes.random_field:
                    cell = randCellState(gui_obj, not_empty_cells_percent_approx)

            tmp.append(cell)

        field.append(tmp)

    return field


def calcScreenSize(grid_size: Vector2, cell_size: Vector2) -> Vector2:
    return Vector2(grid_size.x * cell_size.x, grid_size.y * cell_size.y)


def main():
    print("You can draw on your own if you stop the game processing")
    MAX_FPS = 144
    GRID_SIZE = Vector2(18, 18)
    CELL_SIZE = Vector2(40, 40)
    CELL_MARGIN = Vector2(0, 0)
    # GRID_THICKNESS = round(0.08 * (CELL_SIZE.x + CELL_SIZE.y) / 2)
    GRID_THICKNESS = 0
    NOT_EMPTY_CELLS_PERCENT_APPROX = 30
    MAX_GAME_ITERATIONS_PER_SECOND = 10
    PERFORM_ACTIONS_IN_PLACE = False
    START_MODE = constants.StartModes.random_field

    screen_size = calcScreenSize(GRID_SIZE, CELL_SIZE)

    gui_drawer = gui.classes.GUI_Drawer(screen_size, GRID_SIZE, GRID_THICKNESS, MAX_FPS)
    field = initField(gui_drawer.screen, GRID_SIZE, CELL_SIZE, CELL_MARGIN, NOT_EMPTY_CELLS_PERCENT_APPROX, START_MODE)

    game = Game(gui_drawer, field, MAX_GAME_ITERATIONS_PER_SECOND, PERFORM_ACTIONS_IN_PLACE)

    game.runGUI_threaded()
    game.runGame()


main()
