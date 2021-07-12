"""Game components."""
import logging
import os
import time
from typing import Iterable, Iterator, Union

import blessed
import numpy as np
import pytweening as pt
from blessed.colorspace import X11_COLORNAMES_TO_RGB, RGBColor
from blessed.keyboard import Keystroke

from utils import Vec  # type: ignore

if "logs" not in os.listdir():
    os.mkdir("logs")
logging.basicConfig(filename="logs/debug.log", level=logging.DEBUG)

NEXT_SCENE = 1
RESET = 2
QUIT = 3

term = blessed.Terminal()


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
        colour: RGBColor = X11_COLORNAMES_TO_RGB["aqua"],
        speed: Vec = Vec(2, 1),
    ) -> None:

        self.coords = coords
        self.fill = fill
        self.colour = colour
        self.speed = speed
        self.term = term
        self.commands = {"r": self.render, "c": self.clear}

    def move(self, direction: str) -> str:
        """Moves the cursor to a new position based on direction and speed"""
        render_string = ""
        render_string += self.clear()
        directions = self.directions[direction]
        self.coords.x = min(
            max(self.coords.x + directions.x * self.speed.x, 0), self.term.width - 2
        )
        self.coords.y = min(
            max(self.coords.y + directions.y * self.speed.y, 0), self.term.height - 2
        )
        render_string += self.render()
        return render_string

    def clear(self) -> str:
        """Clears the rendered cursor"""
        return f"{self.term.move_xy(*self.coords)}" + " " * len(self.fill)

    def render(self) -> str:
        """Renders the cursor"""
        render_string = ""
        render_string += f"{self.term.move_xy(*self.coords)}"
        render_string += f"{self.term.color_rgb(*self.colour)}"
        render_string += f"{self.fill}{self.term.normal}"
        return render_string


class Scene:
    """This should be subclassed to create each new level.

    The subclass should implement the functions `rest` and `next_frame`
    """

    def __init__(self):
        self.height = term.height
        self.width = term.width
        self.current_frame = ""

    def reset(self) -> None:
        """Reset the current scene/level to its initial state."""

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame in the scene."""


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
                val = term.inkey(timeout=0.05)  # 20 fps


class Camera:
    """Main Camera Class. Can Have Multiple Cameras in multiplayer"""

    def __init__(
        self,
        game_map: np.ndarray,
        cam_x: int = 0,
        cam_y: int = 0,
        quickness: float = 0.0,
    ) -> None:
        """Initialization of the Camera

        :param cam_x: initial position of camera's x coordinates
        :param cam_y: initial position of camera's y coordinates
        :param game_map: The whole game map
        :param quickness: how fast camera should transition from one point to another
        """
        self.game_map = game_map
        self._cam_x = cam_x
        self._cam_y = cam_y
        self.quickness = quickness

    @property
    def cam_x(self) -> int:
        """:return: camera's x coordinate"""
        return self._cam_x

    @property
    def cam_y(self) -> int:
        """:return: camera's y coordinate"""
        return self._cam_y

    @cam_x.setter  # type: ignore
    def cam_x(self, value: int) -> None:
        pass

    def _set_pos(self, x: int, y: int) -> None:
        interval = 1 * (1 - self.quickness)
        transtion_lenght = int(1 / interval)
        for i in range(transtion_lenght):
            time.sleep(interval)
            self._cam_x *= pt.easeInOutSine(interval * i)
            self._cam_y *= pt.easeInOutSine(interval * i)

    def _render(self, x: int, y: int) -> None:
        # Todo: create the render func and handle errors
        pass
