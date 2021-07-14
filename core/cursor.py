from __future__ import annotations

import time
from copy import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.maze import Maze

from blessed import Terminal
from blessed.keyboard import Keystroke

from core.sound import play_enter_box_sound, play_hit_wall_sound
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

    def __init__(self, coords: Vec, fill: str = "██", speed: Vec = Vec(2, 1),) -> None:

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


class Player:
    """Player class, controls player movement and scores"""

    def __init__(self, start: Vec):
        self.start_loc = start
        self.avi = Cursor(start, fill="█", speed=Vec(1, 1))
        self.score: int = 0
        self.timer_start: float = None
        self.collision_count = 0
        self.prev_colsn_time = time.time()

    def start(self) -> None:
        """Called when the game is started"""
        self.avi.coords = self.start_loc
        self.avi.render()

    def update(self, val: Keystroke, maze: Maze) -> None:
        """Handle player movement"""
        avi_loc = self.avi.loc_on_move(val.name)

        if self.wall_at(avi_loc, maze, val.name):
            collision_time = time.time()
            if collision_time - self.prev_colsn_time > 0.5:
                # collision counter
                self.collision_count += 1
                self.prev_colsn_time = collision_time
                txt = term.home + f"Collisions: {self.collision_count}"
                render(txt, col="black")

                # play sound
                play_hit_wall_sound(avi_loc - self.avi.coords)
        else:
            self.avi.move(val.name)

    def wall_at(self, screen: Vec, maze: Maze, direction: str) -> bool:
        """Return True if there is a wall at (x, y). Values outside the valid range always return False."""
        x, y = maze.screen2mat(screen)
        screen = screen - maze.top_left_corner
        # logging.info(
        #     f"{x=}\t{screen.x=}\t{self.maze.matrix[y][x]}, {self.maze.matrix[y][x-1]}, {self.maze.matrix[y][x+1]}"
        # )
        if 0 <= x < len(maze.matrix[0]) and 0 <= y < len(maze.matrix):
            is_wall = maze.matrix[y][x] == 1
            if is_wall and screen.x == 2 * x + 1:
                if direction == "KEY_LEFT":
                    return False
                if direction == "KEY_DOWN" and maze.matrix[y][x + 1] == 0:
                    return False
                if direction == "KEY_UP" and maze.matrix[y][x + 1] == 0:
                    return False
            return is_wall
        else:
            return False

    def render(self) -> None:
        """Draw player on screen"""
        self.avi.render()

    def enter_box(self) -> None:
        """Called when player enter a box"""
        play_enter_box_sound()

    def hit_wall(self) -> None:
        """Called when player hits wall"""
