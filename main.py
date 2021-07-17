import sys
from typing import List

from openal import oalQuit

from core.sound import play_start_bgm
from game import Game, Scene
from levels import (
    EndScene, Level, credit_scene, leaderboard_menu, pause_menu, title_scene
)

if __name__ == "__main__":
    play_start_bgm()
    scenes: List[Scene] = [title_scene]
    if len(sys.argv) == 1:
        scenes.extend([Level(str(i)) for i in range(1, 9)])
    else:
        scenes.append(Level(sys.argv[1]))
    game = Game(
        scenes,
        pause=pause_menu,
        leaderboard=leaderboard_menu,
        tutorial=Level("0"),
        end_scene=EndScene(),
        credit=credit_scene,
    )
    game.run()
    oalQuit()
