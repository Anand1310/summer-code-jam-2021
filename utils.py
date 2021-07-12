# type: ignore
"""Collection of utilities."""
from cmath import sqrt
from typing import Iterable, Tuple, Union

import numpy as np


class Vec(np.ndarray):
    """2D vector class that can be used with `int` and `(int, int)` for arithmetic."""

    def __new__(cls, x: int, y: int):
        """Create new array."""
        obj = super().__new__(
            cls, (2,), np.int16, np.asarray((x, y)), offset=0, strides=None, order=None
        )
        obj.x = int(x)
        obj.y = int(y)
        return obj

    @property
    def x(self) -> int:
        """Get value of x as first co-ordinate"""
        return int(self[0])

    @property
    def y(self) -> int:
        """Get value of y as first co-ordinate"""
        return int(self[1])

    @x.setter
    def x(self, x: Union[int, float]) -> None:
        """Set value of x as first co-ordinate."""
        self[0] = int(x)

    @y.setter
    def y(self, y: Union[int, float]) -> None:
        """Set value of y as first co-ordinate."""
        self[1] = int(y)

    def __iter__(self) -> Iterable:
        return map(int, (self.x, self.y))


def calc_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """Return the distance between two point"""
    return abs(sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))
