"""Game components."""
import logging
import os
from typing import List, Union

import blessed
from blessed.keyboard import Keystroke

from core.player import Player
from core.render import Render

if "logs" not in os.listdir():
    os.mkdir("logs")
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # or whatever
handler = logging.FileHandler("logs/debug.log", "w", "utf-8")  # or whatever
handler.setFormatter(logging.Formatter("%(name)s %(message)s"))  # or whatever
root_logger.addHandler(handler)
logging.info("=" * 15)

NEXT_SCENE = 1
RESET = 2
QUIT = 3
PAUSE = 4
PLAY = 5
LOSE = 6
CREDITS = 7
TITLE = 0

term = blessed.Terminal()

render = Render()


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


class Game:
    """Main game class. Should be initiated with a list of scenes."""

    def __init__(self, scenes: List[Scene], pause: Scene) -> None:
        self.scenes = scenes
        self.current_scene_index: int = 0
        self.pause = pause
        self.current_scene: Scene = self.scenes[self.current_scene_index]
        self.player = Player()

    def run(self) -> None:
        """Run the main game loop."""
        with term.cbreak():
            val = Keystroke()
            while True:

                command = self.current_scene.next_frame(val)
                # get all the frames and print
                frame = render.screen()
                print(frame)
                if command == NEXT_SCENE:
                    self.current_scene.reset()
                    self.current_scene_index += 1
                    # end game if scenes end
                    if self.current_scene_index == len(self.scenes)-1:
                        break
                    else:
                        self.current_scene = self.scenes[self.current_scene_index]

                        # if self.current_scene_index == len(self.scenes) - 2:
                        #     self.current_scene.set_player(self.player)
                        continue
                elif command == RESET:
                    self.current_scene.reset()
                    val = Keystroke()
                    continue
                elif command == PAUSE:
                    self.current_scene = self.pause
                    continue
                elif command == PLAY:
                    self.pause.reset()
                    self.current_scene = self.scenes[self.current_scene_index]
                    self.current_scene.render(hard=True)
                    continue
                elif command == CREDITS:
                    self.current_scene.reset()
                    self.current_scene = self.scenes[-1]
                    self.current_scene.next_frame(Keystroke())
                elif command == TITLE:
                    self.current_scene.reset()
                    self.current_scene = self.scenes[0]
                    self.current_scene.next_frame(Keystroke())
                elif command == QUIT or command == LOSE:
                    break
                val = term.inkey(timeout=0.05)  # 20 fps
