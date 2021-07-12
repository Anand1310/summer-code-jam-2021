from game import Game
from levels import EndScene, Level_1, Level_2, TitleScene

if __name__ == "__main__":
    game = Game([TitleScene(), Level_1(), Level_2(), EndScene()])
    game.run()
