
# type: ignore
from typing import Any, Union

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

    def __iter__(self) -> Any:
        return map(int, (self.x, self.y))
