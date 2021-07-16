from __future__ import annotations

from blessed import Terminal

from utils import Vec  # type: ignore

term = Terminal()


class Character:
    """Represents a character on screen"""

    __slots__ = "ch", "z_id", "col", "bg_col"

    def __init__(
        self, ch: str, z_id: int, col: str = "black", bg_col: str = "skyblue"
    ) -> None:
        self.ch = ch
        self.z_id = z_id
        self.col = col
        self.bg_col = bg_col

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Character):
            raise ValueError(f"Can't compare Character with {type(other)}")
        return self.z_id == other.z_id

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Character):
            raise ValueError(f"Can't compare Character with {type(other)}")
        return self.z_id <= other.z_id


clean = Character(ch=" ", z_id=-1, col="", bg_col="")
blank = Character(ch="", z_id=0, col="", bg_col="")


class Pixel:
    """Each pixel on terminal"""

    def __init__(
        self,
        char: Character = clean,
        location: Vec = Vec(1, 1),
    ):
        self._char = char
        self._location = location
        self._bg_col: str = None
        self._col: str = None
        self.paint = None
        self.ball_holding_count = 0

    @property
    def char(self) -> Character:
        """Get current character"""
        return self._char

    @char.setter
    def char(self, value: Character) -> None:
        """Set current character"""
        if value.ch == " ":
            self._char = value
        elif self._char <= value:
            self._char = value
            self.col = value.col
            self.bg_col = value.bg_col

    @property
    def col(self) -> str:
        """Get color"""
        return self._col

    @col.setter
    def col(self, val: str) -> None:
        """Set color"""
        self._col = val
        self.paint = getattr(term, f"{self.col}_on_{self.bg_col}")

    @property
    def bg_col(self) -> str:
        """Get background color"""
        return self._bg_col

    @bg_col.setter
    def bg_col(self, val: str) -> None:
        """Set background color"""
        self._bg_col = val
        self.paint = getattr(term, f"{self.col}_on_{self.bg_col}")

    def __str__(self):
        if self._char.ch == " ":
            self._char = blank
            return term.move_xy(*self._location) + " "
        elif self._char.ch == "":
            return ""
        else:
            return term.move_xy(*self._location) + self.paint(self.char.ch)

    def __add__(self, other: object) -> str:
        return str(self) + str(other)
