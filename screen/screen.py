import numpy as np
from blessed import Terminal

from screen.character import Pixel
from utils import Vec  # type: ignore

term = Terminal()


class Screen(object):
    """This represents the screen of the terminal"""

    __monostate = None

    def __init__(self, col: str = "black", bg_col: str = "lightskyblue1"):
        if not Screen.__monostate:
            Screen.__monostate = self.__dict__
            self.scr: np.ndarray = np.ndarray(
                (term.height - 1, term.width - 1), dtype=Pixel
            )
            self.shape = Vec(term.width, term.height)
            self.col = col
            self.bg_col = bg_col
            for i in range(term.height - 1):
                for j in range(term.width - 1):
                    self.scr[i, j] = Pixel(location=Vec(j, i))
        else:
            self.__dict__ = Screen.__monostate

    def get(self) -> str:
        """Get current frame."""
        frame = term.home
        for i in range(term.height - 1):
            for j in range(term.width - 1):
                frame += str(self.scr[i, j])  # type: ignore
        return frame
