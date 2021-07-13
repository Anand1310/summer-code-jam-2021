"""Game components."""
import logging
import os
from copy import copy
from typing import Callable, Iterable, Iterator, List, Union

import blessed
import numpy as np
import pytweening as pt
from blessed.keyboard import Keystroke

from core.sound import play_enter_box_sound, play_hit_wall_sound
from utils import Vec  # type: ignore

if "logs" not in os.listdir():
    os.mkdir("logs")
logging.basicConfig(filename="logs/debug.log", level=logging.DEBUG)
logging.info("=" * 15)

NEXT_SCENE = 1
RESET = 2
QUIT = 3

term = blessed.Terminal()


class Scene:
    """This should be subclassed to create each new level.

    The subclass should implement the functions `rest` and `next_frame`
    """

    def __init__(self, col: str = "black", bg_col: str = "peachpuff2"):
        self.height = term.height
        self.width = term.width
        self.current_frame = ""
        self.col = col
        self.bg_col = bg_col

    def reset(self) -> None:
        """Reset the current scene/level to its initial state."""

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame in the scene."""

    def render(self, frame: str, col: str = None, bg_col: str = None) -> str:
        """Adds font color and background color on text"""
        if col is None:
            col = self.col
        if bg_col is None:
            bg_col = self.bg_col

        paint: Callable[[str], str] = getattr(term, f"{col}_on_{bg_col}")
        bg = getattr(term, f"on_{bg_col}")
        return paint(frame) + bg


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
        render: Callable = Scene().render,
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
        self.last_move = directions
        x = min(
            max(self.prev_coords.x + directions.x * self.speed.x, 0),
            self.term.width - 2,
        )
        y = min(
            max(self.prev_coords.y + directions.y * self.speed.y, 0),
            self.term.height - 2,
        )
        return Vec(x, y)

    def move(self, direction: str) -> str:
        """Move the cursor to a new position based on direction and speed."""
        self.coords = self.loc_on_move(direction)
        return self.clear()

    def clear(self) -> str:
        """Clears the rendered cursor"""
        frame = f"{self.term.move_xy(*self.prev_coords)}" + " " * len(self.fill)
        return frame

    def render(self) -> str:
        """Renders the cursor"""
        self.prev_coords = copy(self.coords)
        frame = ""
        frame += self.term.move_xy(*self.coords)
        frame += self.scene_render(self.fill)
        return frame

    def enter_box(self) -> None:
        """Called when player enter a box"""
        txt = term.home + "pow!"
        play_enter_box_sound()
        print(txt)
        txt = term.home + "    "
        print(term.normal)

    def hit_wall(self) -> None:
        """Called when player hits a wall"""
        txt = term.home + "ouch!"
        play_hit_wall_sound(self.last_move)
        print(txt)
        txt = term.home + "    "
        print(term.normal)


class Game:
    """Main game class. Should be initiated with a list of scenes."""

    def __init__(self, scenes: Iterable[Scene]) -> None:
        self.scenes: Iterator = iter(scenes)
        self.current_scene: Scene = next(self.scenes)

    def run(self) -> None:
        """Run the main game loop."""
        with term.cbreak():
            val = Keystroke()
            while (val.lower() != "q") or (val.lower != "x"):
                # user input
                try:
                    command = self.current_scene.next_frame(val)
                except AttributeError as e:
                    logging.info(f"game ended with {e}")
                    print("Game ended.")
                    break
                if isinstance(command, str):
                    # do not need to print anything if '' is returned
                    if len(command) != 0:
                        print(command)
                elif command == NEXT_SCENE:
                    self.current_scene = next(self.scenes, None)
                    continue
                elif command == RESET:
                    self.current_scene.reset()
                    val = Keystroke()
                    continue
                elif command == QUIT:
                    break
                val = term.inkey(timeout=0.05)  # 20 fps


class Camera:
    """Main Camera Class. Can Have Multiple Cameras in multiplayer"""

    def __init__(
        self,
        game_map: np.ndarray,
        cam_x: int = 0,
        cam_y: int = 0,
        camera_size: int = 100,
        quickness: float = 0.0,
    ) -> None:
        """Initialization of the Camera

        :param cam_x: initial position of camera's x coordinates
        :param cam_y: initial position of camera's y coordinates
        :param camera_size: Pov size
        :param game_map: The whole game map
        :param quickness: how fast camera should transition from one point to another
        """
        self.game_map = game_map
        self.cam_x = cam_x
        self.cam_y = cam_y
        self.camera_size = camera_size
        self.quickness = quickness

    def set_position_styled(self, x: int, y: int) -> List:
        """
        Transition coordinates

        :param x: x coordinate to move to
        :param y: y coordinate to move to
        :return: list of coordinates of animation
        """
        transtion_lenght = int(1 / 0.1)
        interval = 10
        cx = self.cam_x
        cy = self.cam_y
        diff_x = x - cx
        diff_y = y - cy
        animation_coords = []
        for i in range(transtion_lenght):
            cx = cx + pt.easeInOutSine((1 / interval) * i) * diff_x
            cy = cy + pt.easeInOutSine((1 / interval) * i) * diff_y
            animation_coords.append((cx, cy))
        return animation_coords

    def set_position(self, x: int, y: int) -> np.ndarray:
        """
        Set position function

        :param x: x coordinate to move to
        :param y: y coordinate to move to
        :return: player vision
        """

        def clip(x: int, p: int, u: int) -> int:
            return p if x < p else u if x > u else x

        shape = np.shape(self.game_map)
        y_min = clip(0, y, shape[0] - 1)
        y_max = clip(0, y + self.camera_size, shape[0] - 1)
        x_min = clip(0, y, shape[1] - 1)
        x_max = clip(0, y + self.camera_size, shape[1] - 1)
        return self.game_map[y_min:y_max, x_min:x_max]
