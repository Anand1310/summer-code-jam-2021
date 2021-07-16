from __future__ import annotations

from screen.character import Pixel
from screen.screen import Screen
from utils import Vec  # type: ignore


class Widget:
    """Widget class for any objects on screen"""

    def __init__(self) -> None:
        self.top_left: Vec = Vec(1, 1)
        self.screen: Screen = Screen()
        self.screen_shape = Vec(*reversed(self.screen.scr.shape))
        self.shape = Vec(1, 1)

    def __getitem__(self, key: slice) -> Pixel:
        if isinstance(key, Vec):
            return self.screen.scr[key.y, key.x]
        else:
            return self.screen.scr[key]

    def __setitem__(self, key: slice, val: Pixel):
        if isinstance(key, Vec):
            self.screen.scr[key.y, key.x] = val
        else:
            self.screen.scr[key] = val

    def update(self) -> None:
        """Update current state"""


# class Box(Widget):

#     def __init__(self, width: int, height: int, top_left: Vec = None, z_id=1) -> None:
#         super().__init__()
#         self.dash = Character("-", z_id=z_id)
#         self.vert = Character("|", z_id=z_id)
#         self.ball_ch = Character("█", z_id=z_id, col="white")

#         self.shape = Vec(width, height)
#         self.top_left = top_left
#         if self.top_left is None:
#             self.top_left = (self.screen_shape - self.shape) // 2
#         self.bottom_right = self.top_left + self.shape
#         self.ball = Vec(2, 2) + self.top_left
#         self.speed = Vec(1, 1)

#     def update(self):
#         for i in range(0, self.shape.x+1):
#             top_row = self.top_left + Vec(i, 0)
#             bottom_row = self.top_left + Vec(i, self.shape.y)
#             self[top_row].char = self.dash
#             self[bottom_row].char = self.dash
#         for j in range(0, self.shape.y):
#             first_col = self.top_left + Vec(0, j)
#             last_col = self.top_left + Vec(self.shape.x, j)
#             self[first_col].char = self.vert
#             self[last_col].char = self.vert
#         self[self.ball.y, self.ball.x].char = clean

#         # bounce,
#         if self.ball.x <= self.top_left.x or self.ball.x >= self.top_left.x + self.shape.x:
#             self.speed.x *= -1
#         if self.ball.y <= self.top_left.y or self.ball.y >= self.top_left.y + self.shape.y:
#             self.speed.y *= -1

#         # move,
#         self.ball += self.speed

#         self[np.s_[self.ball.y, self.ball.x]].char = self.ball_ch
