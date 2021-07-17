import sys
from typing import List

from openal import oalQuit

from core.sound import play_start_bgm
from game import Game, Scene
from levels import (
    CreditsScene, EndScene, InfiniteLevel, Level, Pause, TitleScene
)

if __name__ == "__main__":
    play_start_bgm()
    scenes: List[Scene] = [TitleScene()]
    scenes.append(InfiniteLevel(True))
    if len(sys.argv) == 1:
        scenes.extend([Level(str(i)) for i in range(9)])
    else:
        scenes.append(Level(sys.argv[1]))
    scenes.append(EndScene())
    scenes.append(CreditsScene())
    game = Game(scenes, pause=Pause())
    game.run()
    oalQuit()
