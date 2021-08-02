from blessed import Terminal

from maze_gitb.core.render import Render
from maze_gitb.utils import Vec  # type: ignore

render = Render()
term = Terminal()


class AnimatedCharacter:
    """Animated character class

    https://www.figma.com/file/KOvD3LAhx8ljCyvNJB4X2e/Untitled?node-id=0%3A1
    """

    def __init__(
        self,
        char: str,
        location: Vec = Vec(1, 1),
        col: str = "black",
        is_visible: bool = True,
    ):
        self.char = char
        self._location = location
        self._col = col
        self._is_visible = is_visible

    def __str__(self):
        return self.char

    def render(self) -> None:
        """Render current character"""
        txt = term.move_xy(*self._location) + self.char
        render(frame=txt, col=self.col)

    @property
    def location(self) -> Vec:
        """Get location of this character"""
        """Get location of this character"""
        return self._location

    @location.setter
    def location(self, val: Vec) -> None:
        """Set location of this character"""
        self._location = val
        self.render()

    @property
    def col(self) -> str:
        """Get colour of this character"""
        return self._col

    @col.setter
    def col(self, val: str) -> None:
        """Set colour of this character"""
        self._col = val
        self.render()

    @property
    def is_visible(self) -> bool:
        """Get visibility of this character"""
        return self._is_visible

    @is_visible.setter
    def is_visible(self, val: bool) -> None:
        """Set visibility of this character"""
        self._is_visible = val
        self.render()
