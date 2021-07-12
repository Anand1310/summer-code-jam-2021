"""Examples for designing levels."""
import copy
import time
from threading import Thread
from typing import Union

import blessed
from blessed.keyboard import Keystroke

from core.maze import Maze
from game import NEXT_SCENE, QUIT, RESET, Cursor, Scene
from utils import Vec  # type: ignore

term = blessed.Terminal()


class TitleScene(Scene):
    """Example of a title scene."""

    def __init__(self) -> None:
        super().__init__()
        txt1 = "welcome to 'Game name' :)"
        txt2 = "hit space to start"
        self.current_frame = term.black_on_peachpuff2 + term.clear
        self.current_frame += term.move_xy(
            x=(self.width - len(txt1)) // 2, y=self.height // 2
        )
        self.current_frame += txt1
        self.current_frame += term.move_xy(
            x=(self.width - len(txt1)) // 2, y=self.height // 2 + 1
        )
        self.current_frame += txt2
        self.first_frame = True

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Returns next frame to render"""
        # no need to update the frame anymore
        if self.first_frame:
            self.first_frame = False
            return self.current_frame
        elif str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return ""

    def reset(self) -> None:
        """Reset has no use for title scene."""
        pass


class Level_1(Scene):
    """Example of a level."""

    def __init__(self) -> None:
        super().__init__()
        self.first_line = term.clear + "hit 'n' to end the game\n" + term.home
        self.first_frame = True

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Return next frame to render"""
        if self.first_frame:
            self.first_frame = False
            print(self.first_line)
        if not val:
            new_line = ""
        elif val.is_sequence:
            new_line = "got sequence: {0}.".format((str(val), val.name, val.code))
        elif val.lower() == "n":
            return NEXT_SCENE
        elif val.lower() == "q":
            return QUIT
        elif val.lower() == "r":
            return RESET
        elif val:
            new_line = "got {0}.".format(val)

        return new_line

    def reset(self) -> None:
        """Reset the current level"""
        self.first_frame = True


class Level_2(Scene):
    """First basic game"""

    def __init__(self) -> None:
        super().__init__()
        self.maze = Maze.load("1")
        self.avi = Cursor(copy.copy(self.maze.start), colour=(0, 0, 0))
        self.first_frame = True
        self.terminal_shape = Vec(term.width, term.height)

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame"""
        if self.first_frame:
            self.first_frame = False
            # removes the main maze after 2 sec
            Thread(target=self.remove_maze, daemon=True).start()
            return term.clear + self.draw_maze(str(self.maze)) + self.avi.render()
        elif val.is_sequence and (257 < val.code < 262):
            return self.avi.next_location(val.name)
        elif val.lower() == "q":
            return QUIT
        elif val.lower() == "r":
            return RESET
        return ""

    def draw_maze(self, maze: str, update_cursor: bool = True) -> str:
        """Draw main maze"""
        maze = maze.split("\n")  # type: ignore
        maze_shape = Vec(len(maze[0]), len(maze))
        start_location = (self.terminal_shape - maze_shape) // 2
        new_line = term.move_left(maze_shape.x) + term.move_down(1)
        maze = new_line.join(maze)
        if update_cursor:
            self.avi.coords += start_location
        return term.move_xy(*start_location) + maze

    def remove_maze(self) -> str:
        """Erase main maze"""
        time.sleep(2)
        maze = str(self.maze)
        for chr in "┼├┴┬┌└─╶┤│┘┐╷╵╴":
            if chr in maze:
                maze = maze.replace(chr, " ")
        erase_maze = self.draw_maze(maze, update_cursor=False)
        draw_avi = self.avi.render()
        print(erase_maze + draw_avi)

    def reset(self) -> None:
        """Reset this level"""
        self.avi.coords = copy.copy(self.maze.start)
        self.first_frame = True


class EndScene(Scene):
    """Example of ending scene."""

    def __init__(self):
        super().__init__()
        txt = "You won :o"
        self.current_frame = term.move_xy(
            x=(self.width - len(txt)) // 2, y=self.height // 2
        )
        self.current_frame += txt
        self.first_frame = True

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Return next frame to render"""
        # no need to update each frame
        if self.first_frame:
            self.first_frame = False
            return self.current_frame
        elif str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return ""

    def reset(self) -> None:
        """No use."""
        pass
