from __future__ import annotations

import time
from copy import copy
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.maze import Maze

import logging

from blessed import Terminal
from blessed.keyboard import Keystroke

from core.render import Render
from core.sound import play_echo, play_enter_box_sound, play_hit_wall_sound
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
        self.direction = Vec(1, 0)
        self.term = term

    def loc_on_move(self, move: str) -> Vec:
        """Find location of cursor on move in direction."""
        self.direction = self.directions[move]
        x = min(
            max(self.prev_coords.x + self.direction.x * self.speed.x, 0),
            self.term.width - 2,
        )
        y = min(
            max(self.prev_coords.y + self.direction.y * self.speed.y, 0),
            self.term.height - 2,
        )
        return Vec(x, y)

    def move(self, move: str) -> None:
        """Move the cursor to a new position based on direction and speed."""
        logging.info("Player position:" + str(self.coords))
        self.coords = self.loc_on_move(move)
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


class Score:
    """Player score"""

    def __init__(self):
        self.value = 200
        self.penalty = 0.05

    def update(
        self, player_inside_box: bool = False, collision_count: int = None
    ) -> None:
        """Update score based on collision count and whether player is inside box"""
        if collision_count:
            self.value -= collision_count * 2
        else:
            # self.value -= self.penalty * (1 + 10 * player_inside_box)
            logging.info("in score")
            logging.info(self.value)
            logging.info(self.penalty * int(not player_inside_box))
            logging.info(player_inside_box)
            self.value -= self.penalty * int(not player_inside_box)
            logging.info(self.value)
        self.render()

    def render(self) -> None:
        """Render score"""
        txt = f"Score:{int(self.value)}"
        txt = term.home + term.move_x(term.width - len(txt)) + txt
        render(txt, col="black")


class Player:
    """Player class, controls player movement and scores"""

    __monostate = None

    def __init__(self, location: Vec = Vec(1, 1)):
        if not Player.__monostate:
            Player.__monostate = self.__dict__
            self.name = ""
            self.start_loc = location
            self.avi = Cursor(location, fill="█", speed=Vec(1, 1))
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
        avi_loc = self.avi.loc_on_move(val.name)

        if self.wall_at(avi_loc, maze, val.name):
            collision_time = time.time()
            if collision_time - self.prev_colsn_time > 0.5:
                # collision counter
                self.collision_count += 1
                self.score.update(collision_count=self.collision_count)
                self.prev_colsn_time = collision_time
                txt = term.home + f"Collisions: {self.collision_count}"
                render(txt, col="black")

                # play sound
                self.hit_wall(avi_loc)
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

    def player_movement_sound(self, maze: Maze) -> None:
        """Make player sound on move"""
        x, y = maze.screen2mat(self.avi.coords)
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
                play_echo(direction, 2 * (nearest_wall.x - x))
            else:
                play_echo(direction, 2 * (nearest_wall.x - x) - 1)
        elif all(direction == (-1, 0)):  # left
            if screen.x == 2 * x:
                play_echo(direction, 2 * (nearest_wall.x - x) - 1)
            else:
                play_echo(direction, 2 * (nearest_wall.x - x))
        else:
            play_echo(direction, nearest_wall.y - y)

    def render(self) -> None:
        """Draw player on screen"""
        self.avi.render()

    def enter_box(self) -> None:
        """Called when player enter a box"""
        play_enter_box_sound()

    # def exit_box(self) -> None:
    #     """Call when player exits a box."""
    #     self.inside_box = False

    def hit_wall(self, avi_loc: Vec) -> None:
        """Called when player hits wall"""
        play_hit_wall_sound(avi_loc - self.avi.coords)
