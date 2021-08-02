from typing import List

from openal import oalQuit

from maze_gitb.core.sound import play_start_bgm
from maze_gitb.game import Game, Scene
from maze_gitb.scene import (
    EndScene, InfiniteLevel, Level, credit_scene, leaderboard_menu, pause_menu,
    title_scene
)


def main() -> None:
    """Run the main program"""
    play_start_bgm()
    scenes: List[Scene] = [title_scene]
    scenes.extend([Level(str(i)) for i in range(1, 9)])
    # if len(sys.argv) == 1:
    #     scenes.extend([Level(str(i)) for i in range(1, 9)])
    # else:
    #     scenes.append(Level(sys.argv[1]))
    game = Game(
        scenes,
        pause=pause_menu,
        infinite=InfiniteLevel(True),
        leaderboard=leaderboard_menu,
        tutorial=Level("0"),
        end_scene=EndScene(),
        credit=credit_scene,
    )
    game.run()
    oalQuit()


if __name__ == "__main__":
    main()
