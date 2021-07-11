import logging
import os
from typing import Iterable, Iterator, Union

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
        """This function should reset the current scene/level to its initial state"""

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Function to draw next frame in the scene"""


class Game:
    """Main game class. Should be initiated with a list of scenes."""

    def __init__(self, scenes: Iterable[Scene]) -> None:
        self.scenes: Iterator = iter(scenes)
        self.current_scene: Scene = next(self.scenes)

    def run(self) -> None:
        """Main game loop"""
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
                    continue

                val = term.inkey(timeout=3)
