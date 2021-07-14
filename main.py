import sys
from typing import List

from game import Game, Scene
from levels import EndScene, Level_2, TitleScene

if __name__ == "__main__":
    scenes: List[Scene] = [TitleScene()]
    if len(sys.argv) == 1:
        scenes.extend([Level_2(str(i)) for i in range(1, 9)])
    else:
        scenes.append(Level_2(sys.argv[1]))
    scenes.append(EndScene())
    game = Game(scenes)
    game.run()
