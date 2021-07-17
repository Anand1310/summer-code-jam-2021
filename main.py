import sys
from typing import List

from openal import oalQuit

from core.sound import play_start_bgm
from game import Game, Scene
from levels import EndScene, Level, Pause, TitleScene

if __name__ == "__main__":
    play_start_bgm()
    scenes: List[Scene] = [TitleScene()]
    if len(sys.argv) == 1:
        scenes.extend([Level(str(i)) for i in range(9)])
    else:
        scenes.append(Level(sys.argv[1]))
    scenes.append(EndScene())
    game = Game(scenes, pause=Pause())
    game.run()
    oalQuit()
