"""Examples for designing levels."""
import logging
import time
from copy import copy
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

    def __init__(self, level: str = "1") -> None:
        super().__init__()
        self.maze = Maze.load(level)

        self.avi = Cursor(Vec(1, 1), render=self.render, fill="█", speed=Vec(1, 1))
        self.first_frame = True
        self.maze_is_visible = False

        maze = str(self.maze).split("\n")
        self.maze_shape = Vec(len(maze[0]), len(maze))
        self.terminal_shape = Vec(term.width, term.height)
        self.top_left_corner = (self.terminal_shape - self.maze_shape) // 2
        self.end_loc = self.maze.end * (2, 1) + self.top_left_corner
        for box in self.maze.boxes:
            # move to top-left corner of maze + scale and extend width
            # + move to top-left corner of box
            box.loc = self.top_left_corner + box.loc * (2, 1) - (1, 1)
            box.scene_render = self.render
            box.top_left_corner = copy(self.top_left_corner)

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame"""
        if self.first_frame:
            self.first_frame = False
            # removes the main maze after 2 sec
            Thread(target=self.remove_maze, daemon=True).start()
            frame = term.clear
            frame += self.draw_maze(self.maze.draw()) + self.avi.render()  # type: ignore
            for box in self.maze.boxes:
                frame += box.render(self.avi)
            frame += term.move_xy(*self.end_loc) + "&"  # type: ignore
            return self.render(frame)

        elif val.is_sequence and (257 < val.code < 262):
            loc_in_maze = self.avi.loc_on_move(val.name) - self.top_left_corner

            frame = ""  # type: ignore
            if self.maze.wall_at(*loc_in_maze):
                self.avi.hit_wall()
                # collision count goes here
                logging.info(f"hit maze @ {self.avi.loc_on_move(val.name)}")
                val = term.inkey()
            elif all(self.avi.coords == self.end_loc):
                return NEXT_SCENE
            else:
                frame += self.avi.move(val.name)  # type: ignore
            for box in self.maze.boxes:
                frame += box.render(self.avi)
            frame += self.avi.render()  # type: ignore
            return self.render(frame)

        elif val.lower() == "q":
            return QUIT
        elif val.lower() == "r":
            return RESET
        elif val.lower() == "h":
            if not self.maze_is_visible:
                self.maze_is_visible = True
                frame = self.draw_maze(self.maze.draw(), update_cursor=False)  # type: ignore
                frame += self.avi.render()  # type: ignore
                return frame
            else:
                self.maze_is_visible = False
                self.remove_maze(0)
                return ""
        return ""

    def draw_maze(self, maze: str, update_cursor: bool = True) -> str:
        """Draw main maze"""
        logging.info(f"{update_cursor=}")
        if update_cursor:
            self.avi.coords = self.top_left_corner + self.maze.start * (2, 1)
        return term.move_xy(*self.top_left_corner) + self.render(maze)

    def remove_maze(self, sleep: float = 2) -> None:
        """Erase main maze"""
        time.sleep(sleep)
        maze = self.maze.draw()
        for chr in "┼├┴┬┌└─╶┤│┘┐╷╵╴":
            if chr in maze:
                maze = maze.replace(chr, " ")
        frame = self.draw_maze(maze, update_cursor=False)  # erase maze
        frame += self.avi.render()  # draw avi
        for box in self.maze.boxes:
            frame += box.render(self.avi)
        print(frame)

    def reset(self) -> None:
        """Reset this level"""
        for box in self.maze.boxes:
            box.needs_cleaning = False
        self.avi.coords = copy(self.maze.start)
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
            return self.render(self.current_frame)
        elif str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return ""

    def reset(self) -> None:
        """No use."""
        pass
