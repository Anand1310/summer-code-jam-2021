"""This file shows some examples to design levels"""


from typing import Union

import blessed
from blessed.keyboard import Keystroke

from game import NEXT_SCENE, QUIT, RESET, Scene

term = blessed.Terminal()


class TitleScene(Scene):
    """Example of a title scene"""

    def __init__(self) -> None:
        super().__init__()
        txt1 = "welcome to 'Game name' :)"
        txt2 = "hit space to start"
        self.current_frame = term.clear
        self.current_frame += term.move_xy(
            x=(self.width - len(txt1)) // 2, y=self.height // 2
        )
        self.current_frame += txt1
        self.current_frame += term.move_xy(
            x=(self.width - len(txt1)) // 2, y=self.height // 2 + 1
        )
        self.current_frame += txt2

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Returns next frame to render"""
        if str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return self.current_frame

    def reset(self) -> None:
        """Reset has no use for title scene"""
        pass


class Level_1(Scene):
    """Example of a level"""

    def __init__(self) -> None:
        super().__init__()
        self.current_frame = term.clear + "hit 'n' to end the game"

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Returns next frame to render"""
        if not val:
            new_line = "It sure is quiet in here ..."
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

        self.current_frame += "\n" + new_line
        return self.current_frame

    def reset(self) -> None:
        """Resets the current level"""
        self.current_frame = term.clear + "hit 'n' to end the game"


class EndScene(Scene):
    """Example of ending scene"""

    def __init__(self):
        super().__init__()
        txt = "You won :o"
        self.current_frame = term.clear
        self.current_frame += term.move_xy(
            x=(self.width - len(txt)) // 2, y=self.height // 2
        )
        self.current_frame += txt

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Returns next frame to render"""
        if str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return self.current_frame

    def reset(self) -> None:
        """No use"""
        pass
