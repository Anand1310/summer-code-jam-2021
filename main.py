import sys
from typing import List

from openal import oalQuit

from core.sound import play_start_bgm
from game import Game, Scene
from levels import (
    EndScene, Leaderboard, Level, credit_scene, pause_menu, title_scene
)

if __name__ == "__main__":
    play_start_bgm()
    scenes: List[Scene] = [title_scene]
    if len(sys.argv) == 1:
        scenes.extend([Level(str(i)) for i in range(9)])
    else:
        scenes.append(Level(sys.argv[1]))
    scenes.append(EndScene())
    scenes.append(credit_scene)
    scenes.append(Leaderboard())
    game = Game(scenes, pause=pause_menu)
    game.run()
    oalQuit()
