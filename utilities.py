from typing import Union

import numpy as np


class Vec(np.ndarray):
    """2d vector class can be used with `int` and `(int, int)` for arithmatic"""

    def __new__(cls, x: int, y: int):
        """Creates new array"""
        obj = super().__new__(
            cls, (2,), np.int16, np.asarray((x, y)), offset=0, strides=None, order=None
        )
        obj.x = int(x)
        obj.y = int(y)
        return obj

    @property
    def x(self) -> int:
        """Get value of x as first co-ordinate"""
        return self[0]

    @property
    def y(self) -> int:
        """Get value of y as first co-ordinate"""
        return self[1]

    @x.setter
    def x(self, x: Union[int, float]) -> None:
        """Set value of x as first co-ordinate"""
        self[0] = int(x)

    @y.setter
    def y(self, y: Union[int, float]) -> None:
        """Set value of y as first co-ordinate"""
        self[1] = int(y)
