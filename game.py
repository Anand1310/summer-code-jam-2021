"""Game components."""
import logging
import os
import time
from typing import Callable, Iterable, Iterator, Union

import blessed
import numpy as np
import pytweening as pt
from blessed.keyboard import Keystroke

from utils import Vec  # type: ignore

if "logs" not in os.listdir():
    os.mkdir("logs")
logging.basicConfig(filename="logs/debug.log", level=logging.DEBUG)

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

        paint = getattr(term, f"{col}_on_{bg_col}")
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

        self.coords = coords
        self.fill = fill
        self.scene_render = render
        self.speed = speed
        self.term = term
        self.commands = {"r": self.render, "c": self.clear}

    def next_location(self, direction: str) -> str:
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
        render_string += self.term.move_xy(*self.coords)
        render_string += self.scene_render(self.fill)
        return render_string

    def hit(self) -> None:
        """Called when player hits something"""
        loc = self.coords - (1, 1)
        txt = term.move_xy(*loc) + "pow!"
        print(txt)
        time.sleep(1)
        txt = term.move_xy(*loc) + "    "
        print(txt)


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
