"""Game components."""
import logging
import os
from typing import Iterable, Iterator, Union

import blessed
import numpy as np
from blessed.keyboard import Keystroke

from utils import Vec

if "logs" not in os.listdir():
    os.mkdir("logs")
logging.basicConfig(filename="logs/debug.log", level=logging.DEBUG)


NEXT_SCENE = 1
RESET = 2
QUIT = 3

term = blessed.Terminal()


class Box:
    """Box where parts of maze become visible."""

    def __init__(self, location: Vec, maze: np.ndarray):
        self.maze = maze

        self.a = location
        self.b = location + Vec(3, 0)
        self.c = self.b + Vec(0, 3)

    def show_maze(self, player_location: Vec) -> str:
        """Return a string that draws the box and associated maze based on player location."""
        AB = self.b - self.a
        BC = self.c - self.b

        proj_AB = np.dot(AB, player_location - self.a)
        proj_BC = np.dot(BC, player_location - self.b)

        # https://stackoverflow.com/a/2763387
        if (
            0 <= proj_AB
            and proj_AB <= np.dot(AB, AB)
            and 0 <= proj_BC
            and proj_BC <= np.dot(BC, BC)
        ):
            return self.maze
        else:
            return ""


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
                elif command == QUIT:
                    break

                val = term.inkey(timeout=0.05)  # 20fps
