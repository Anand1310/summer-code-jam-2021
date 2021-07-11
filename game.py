"""Game components."""
import logging
import os
from typing import Iterable, Iterator, Union
import pytweening as pt
import numpy as np
import time

import blessed
from blessed.keyboard import Keystroke

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

    def __init__(self):
        self.height = term.height
        self.width = term.width
        self.current_frame = term.clear + term.on_peachpuff2

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
            val = term.inkey(timeout=0.01)
            while (val.lower() != "q") or (val.lower != "x"):
                # user input
                try:
                    command = self.current_scene.next_frame(val)
                except AttributeError as e:
                    logging.info(f"game ended with {e}")
                    print("Game ended.")
                    break

                if isinstance(command, str):
                    print(command)
                elif command == NEXT_SCENE:
                    self.current_scene = next(self.scenes, None)
                    continue
                elif command == RESET:
                    self.current_scene.reset()
                    val = Keystroke()
                    continue

                val = term.inkey(timeout=3)


class Camera:
    def __init__(self, game_map: np.ndarray, cam_x: int = 0, cam_y: int = 0, quickness: float = 0.0) -> None:
        """
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
    def cam_x(self):
        return self._cam_x

    @property
    def cam_y(self) -> int:
        return self._cam_y

    @cam_x.setter
    def cam_x(self, value) -> None:
        pass

    def _set_pos(self, x, y) -> None:
        interval = 1 * (1 - self.quickness)
        transtion_lenght = int(1 / interval)
        for i in range(transtion_lenght):
            time.sleep(interval)
            self._cam_x *= pt.easeInOutSine(interval * i)
            self._cam_y *= pt.easeInOutSine(interval * i)

    def _render(self, x, y):
        # Todo: create the render func and handle errors
        pass
