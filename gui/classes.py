import copy
import time

import pygame as pg

import enums
from utils import Vector2


class Colors:
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    purple = (128, 0, 128)
    gray = (128, 128, 128)

class GUI_Object:
    MOUSE_CLICK_ACCEPT_TIME_INTERVAL = 0.2
    def __init__(self, screen: pg.display, pos: Vector2, size: Vector2, color: Colors.__dict__):
        self.screen = screen
        self.pos = pos
        self.size = size
        self.color = color

        self.left_top_bound: Vector2 = copy.copy(self.pos)
        self.right_bottom_bound: Vector2 = Vector2(self.pos.x + self.size.x, self.pos.y + self.size.y)

        self.next_time_mouse_click_accepted = time.time() + self.MOUSE_CLICK_ACCEPT_TIME_INTERVAL

    def checkMouseWithinBounds(self, mouse_pos: Vector2) -> bool:
        if self.left_top_bound.x <= mouse_pos.x <= self.right_bottom_bound.x \
                and self.left_top_bound.y <= mouse_pos.y <= self.right_bottom_bound.y:
            return True
        return False


    def checkMousePressed(self, mouse_click_state: list[int, ...]) -> bool:
        if mouse_click_state[0] and time.time() >= self.next_time_mouse_click_accepted:
            self.next_time_mouse_click_accepted = time.time() + self.MOUSE_CLICK_ACCEPT_TIME_INTERVAL
            return True
        return False

    def draw(self) -> None:
        pass

    def update(self) -> Ellipsis:
        pass

class Cell(GUI_Object):
    def __init__(self, screen: pg.display, pos: Vector2, size: Vector2, inactive_color: Colors.__dict__, active_color: Colors.__dict__, border_width: int = 0):
        super().__init__(screen, pos, size, inactive_color)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.border_width = border_width
        self.inner_rect_size = self.size - Vector2(border_width, border_width)
        self.inner_rect_pos = self.pos + Vector2(border_width // 2, border_width // 2)

    def setActive(self):
        self.color = self.active_color

    def setInactive(self):
        self.color = self.inactive_color

    def draw(self) -> None:
        pg.draw.rect(self.screen, self.active_color, (self.pos.getTuple(), self.size.getTuple()))
        pg.draw.rect(self.screen, self.color, (self.inner_rect_pos.getTuple(), self.inner_rect_size.getTuple()))

    def update(self) -> Ellipsis:
        self.draw()


class Grid(GUI_Object):
    def __init__(self, screen: pg.display, pos: Vector2, size: Vector2, color: Colors.__dict__, grid_size: Vector2, thickness: int):
        super().__init__(screen, pos, size, color)
        self.grid_size = grid_size
        self.thickness = thickness
        self.lines = []
        for i in range(1, grid_size.x):
            self.lines.append(((self.size.x // grid_size.x * i + self.pos.x, 0 + self.pos.y), (self.size.x // grid_size.x * i + self.pos.x, self.size.y + self.pos.y)))
        for i in range(1, grid_size.y + 1):
            self.lines.append(((0 + self.pos.x, self.size.y // grid_size.y * i + self.pos.y), (self.size.x + self.pos.x, self.size.x // grid_size.x * i + self.pos.y)))


    def draw(self):
        for line in self.lines:
            pg.draw.line(self.screen, self.color, line[0], line[1], self.thickness)


    def update(self) -> Ellipsis:
        self.draw()

class Menu(GUI_Object):

    def __init__(self, screen: pg.display, pos: Vector2, size: Vector2, color: Colors.__dict__, menu_layout: dict):
        super().__init__(screen, pos, size, color)

        self.buttons = []
        self.texts = []
        for k, v in menu_layout.items():
            obj = v["obj"]
            state = v["state"]
            gui_kwargs = v["gui_kwargs"]
            gui_kwargs["pos"] += pos
            gui_obj = Cell(self.screen, inactive_color=Colors.black, active_color=Colors.purple, **gui_kwargs)
            btn = obj(gui_obj, state)

            self.texts.append(k)

            self.buttons.append(btn)



    def draw(self) -> None:
        pass

    def update(self):
        self.draw()


class GUI_Drawer:
    def __init__(self, grid_size: Vector2, grid_thickness: int, cell_size: Vector2, menu_size: Vector2, menu_layout: dict, max_fps: int = 60):
        pg.init()
        self.pg_events = pg.event.get()
        pg.font.init()
        self.pg_font = pg.font.SysFont('Roboto Mono', 20)

        grid_screen_size = grid_size * cell_size

        menu_size.x = grid_screen_size.x

        self.screen_size = grid_size * cell_size
        self.screen_size.y += menu_size.y

        self.screen = pg.display.set_mode(self.screen_size.getTuple())
        self.clock = pg.time.Clock()
        self.__max_fps = max_fps

        self.grid = Grid(self.screen,  Vector2(0, 0), grid_screen_size, Colors.white, grid_size, grid_thickness)
        self.menu = Menu(self.screen, Vector2(0, self.screen_size.y - menu_size.y), menu_size, Colors.white, menu_layout)

    def renderCurrentStateText(self, text: str, text_pos: Vector2):
        text_surface = self.pg_font.render(text, True, Colors.white)
        self.screen.blit(text_surface, text_pos.getTuple())

    def setMaxFPS(self, max_fps: int):
        self.__max_fps = max_fps

    def drawGrid(self):
        self.grid.update()

    def drawMenu(self):
        self.menu.update()


    def drawStartMenu(self):
        self.start_menu.update()

    def clearScreen(self, color: Colors.__dict__ = Colors.black):
        self.screen.fill(color)

    def updateScreen(self):
        pg.display.update()
        self.clock.tick(self.__max_fps)



if __name__ == "__main__":
    tmp_vec = Vector2(2, 14)
    tmp_vec2 = Vector2(10, 10)
    tmp_vec3 = tmp_vec + tmp_vec2
    print(tmp_vec)
    print(tmp_vec2)
    print(tmp_vec + tmp_vec2)
    print(tmp_vec3)
    print(tmp_vec)
    print(tmp_vec2)