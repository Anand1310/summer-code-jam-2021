import sys
from typing import List

from game import Game, Scene
from levels import EndScene, Level, TitleScene

if __name__ == "__main__":
    scenes: List[Scene] = [TitleScene()]
    if len(sys.argv) == 1:
        scenes.extend([Level(str(i)) for i in range(1, 5)])

    else:
        scenes.append(Level(sys.argv[1]))
    scenes.append(EndScene())
    game = Game(scenes)
    game.run()
