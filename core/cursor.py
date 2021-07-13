from copy import copy

from blessed import Terminal

from game import Render
from utils import Vec  # type: ignore

term = Terminal()
render = Render()


class Cursor:
    """Creates a Cursor Object that can be moved on command"""

    directions = {
        "KEY_UP": Vec(0, -1),
        "KEY_DOWN": Vec(0, 1),
        "KEY_LEFT": Vec(-1, 0),
        "KEY_RIGHT": Vec(1, 0),
    }

    def __init__(
        self,
        coords: Vec,
        fill: str = "██",
        speed: Vec = Vec(2, 1),
    ) -> None:

        self.prev_coords = coords
        self.coords = coords
        self.fill = fill
        self.scene_render = render
        self.speed = speed
        self.term = term

    def loc_on_move(self, direction: str) -> Vec:
        """Find location of cursor on move in direction."""
        directions = self.directions[direction]
        x = min(
            max(self.prev_coords.x + directions.x * self.speed.x, 0),
            self.term.width - 2,
        )
        y = min(
            max(self.prev_coords.y + directions.y * self.speed.y, 0),
            self.term.height - 2,
        )
        return Vec(x, y)

    def move(self, direction: str) -> None:
        """Move the cursor to a new position based on direction and speed."""
        self.coords = self.loc_on_move(direction)
        self.clear()

    def clear(self) -> None:
        """Clears the rendered cursor"""
        frame = f"{self.term.move_xy(*self.prev_coords)}" + " " * len(self.fill)
        render(frame)
        # return frame

    def render(self) -> None:
        """Renders the cursor"""
        self.prev_coords = copy(self.coords)
        frame = self.term.move_xy(*self.coords) + self.fill
        render(frame, col="black", bg_col="white")
