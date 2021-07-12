"""Examples for designing levels."""
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
    """pepeHands"""

    def __init__(self) -> None:
        super().__init__()
        self.maze = Maze.load("1")
        self.avi = Cursor(Vec(1, 2))


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
