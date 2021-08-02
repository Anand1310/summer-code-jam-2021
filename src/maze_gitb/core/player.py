from __future__ import annotations

import time
from copy import copy
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from maze_gitb.core.maze import Maze

from blessed import Terminal
from blessed.keyboard import Keystroke

from maze_gitb.core.render import Render
from maze_gitb.core.sound import (
    play_echo, play_enter_box_sound, play_hit_wall_sound
)
from maze_gitb.utils import Vec  # type: ignore

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
        col: str = "black",
        bg_col: str = "white",
    ) -> None:

        self.prev_coords = coords
        self.coords = coords
        self.fill = fill
        self.scene_render = render
        self.speed = speed
        self.direction = Vec(1, 0)
        self.term = term
        self.col = col
        self.bg_col = bg_col

    def move(self, move: str) -> None:
        """Move the cursor to a new position based on direction and speed."""
        self.direction = self.directions[move]
        self.coords.x = min(
            max(self.prev_coords.x + self.direction.x * self.speed.x, 0),
            self.term.width - 2,
        )
        self.coords.y = min(
            max(self.prev_coords.y + self.direction.y * self.speed.y, 0),
            self.term.height - 2,
        )
        self.clear()

    def stop(self) -> None:
        """Stop current move and go back"""
        self.coords = copy(self.prev_coords)

    def clear(self) -> None:
        """Clears the rendered cursor"""
        frame = f"{self.term.move_xy(*self.prev_coords)}" + " " * len(self.fill)
        render(frame, bg_col=self.bg_col)

    def render(self) -> None:
        """Renders the cursor"""
        self.prev_coords = copy(self.coords)
        frame = self.term.move_xy(*self.coords) + self.fill
        render(frame, col=self.col, bg_col=self.bg_col)


class Score:
    """Player score"""

    def __init__(self):
        self.value = 200
        self.init_value = self.value
        self.penalty = 0.05

    def update(
        self, player_inside_box: bool = False, collision_count: int = None
    ) -> None:
        """Update score based on collision count and whether player is inside box"""
        if collision_count:
            self.value -= collision_count * 2
        else:
            # self.value -= self.penalty * (1 + 10 * player_inside_box)
            if player_inside_box:
                self.value -= self.penalty / 2
            else:
                self.value -= self.penalty
        self.render()

    def render(self) -> None:
        """Render score"""
        txt = f"Persistence: {str(int(self.value)).zfill(3)}"
        txt = term.home + term.move_x(term.width - 18) + txt
        render(txt, col="black")


class Player:
    """Player class, controls player movement and scores"""

    __monostate = None

    def __init__(self, location: Vec = Vec(1, 1)):
        if not Player.__monostate:
            Player.__monostate = self.__dict__
            self.start_loc = location
            self.avi = Cursor(
                location, fill="█", speed=Vec(1, 1), bg_col="lightskyblue1"
            )
            self.score: Score = Score()
            self.timer_start: float = None
            self.collision_count = 0
            self.prev_colsn_time = time.time()
            self.inside_box: Dict[str, bool] = {}
        else:
            self.__dict__ = Player.__monostate

    def start(self) -> None:
        """Called when the game is started"""
        self.avi.coords = self.start_loc
        self.avi.render()
        self.score.update()

    def update(self, val: Keystroke, maze: Maze) -> None:
        """Handle player movement"""
        self.avi.move(val.name)

        if self.wall_at(self.avi.coords, maze, val.name):
            collision_time = time.time()
            if collision_time - self.prev_colsn_time > 0.5:
                # collision counter
                self.collision_count += 1
                self.score.update(collision_count=self.collision_count)
                self.prev_colsn_time = collision_time
                txt = term.home + f"Collisions: {self.collision_count}"
                render(txt, col="black")

                # play sound
                play_hit_wall_sound(self.avi.coords - self.avi.prev_coords)
            self.avi.stop()

    def wall_at(self, screen: Vec, maze: Maze, direction: str) -> bool:
        """Return True if there is a wall at (x, y). Values outside the valid range always return False."""
        screen = screen - maze.top_left_corner
        return maze.char_matrix[screen.y][screen.x].char != " "

    def player_movement_sound(self, maze: Maze) -> None:
        """Make player sound on move"""
        y, x = maze.screen2mat(self.avi.coords)
        screen = self.avi.coords - maze.top_left_corner
        nearest_wall = Vec(x, y)
        direction = copy(self.avi.direction)
        wall_found = False

        while not wall_found:
            if (
                nearest_wall.x >= len(maze.matrix[0]) - 1
                or nearest_wall.y >= len(maze.matrix) - 1
            ):
                break
            nearest_wall += direction
            wall_found = maze.matrix[nearest_wall.y][nearest_wall.x] == 1

        if all(direction == (1, 0)):  # right
            if screen.x == 2 * x:
                self._play_echo(direction, 2 * (nearest_wall.x - x))
            else:
                self._play_echo(direction, 2 * (nearest_wall.x - x) - 1)
        elif all(direction == (-1, 0)):  # left
            if maze.matrix[y][x] == 1:
                play_echo(direction, -1)
            elif screen.x == 2 * x:
                play_echo(direction, 2 * (nearest_wall.x - x) - 1)
            else:
                self._play_echo(direction, 2 * (nearest_wall.x - x))
        else:
            self._play_echo(direction, nearest_wall.y - y)

    def _play_echo(self, direction: Vec, distance: float) -> None:
        play_echo(direction, distance)

    def render(self) -> None:
        """Draw player on screen"""
        self.avi.render()

    def enter_box(self) -> None:
        """Called when player enter a box"""
        play_enter_box_sound()

    def hit_wall(self) -> None:
        """Called when player hits wall"""


class MenuCursor(Cursor):
    """Menu Cursor that moves up and down"""

    def __init__(
        self,
        coords: Vec,
        bounds: Vec,
        options: list,
        fill: str = "->",
        col: str = "black",
        bg_col: str = "peachpuff2",
    ) -> None:
        super().__init__(coords, fill=fill, col=col, bg_col=bg_col)
        self.l_bounds = copy(coords)
        self.u_bounds = coords + bounds
        self.bounds = bounds
        self.options = options
        self.selected = 0

    def move(self, direction: str) -> None:
        """A bounded move method"""
        super(MenuCursor, self).move(direction)
        new_loc = self.coords
        if any(self.l_bounds > new_loc) or any(new_loc > self.u_bounds):
            self.stop()
        else:
            self.selected += self.directions[direction].y
