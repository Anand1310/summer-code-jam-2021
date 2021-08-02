from typing import Callable, List

from blessed import Terminal


class Render(object):
    """Render class to put things on the screen

    This class can be instantiated anywhere.
    Example:
        ```
        from maze_gitb.core.render import Render

        render = Render()
        render("this text", col="black", bg_col="lightskyblue1")
        ```
    """

    __monostate = None

    def __init__(self, col: str = "black", bg_col: str = "lightskyblue1"):
        if not Render.__monostate:
            Render.__monostate = self.__dict__
            self.frames: List[str] = [""]
            self.term = Terminal()
            self.col = col
            self.bg_col = bg_col

        else:
            self.__dict__ = Render.__monostate

    def __call__(self, frame: str, col: str = None, bg_col: str = None) -> None:
        """Adds font color and background color on text"""
        if col is None:
            col = self.col
        if bg_col is None:
            bg_col = self.bg_col

        paint: Callable[[str], str] = getattr(self.term, f"{col}_on_{bg_col}")
        bg = getattr(self.term, f"on_{self.bg_col}")
        frame = self.term.home + paint(frame) + bg
        self.frames.append(frame)

    def screen(self) -> str:
        """Get all the frames."""
        frame = "".join(self.frames) + self.term.home
        self.frames = [""]
        return frame
