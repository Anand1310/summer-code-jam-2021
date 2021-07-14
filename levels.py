"""Examples for designing levels."""
import time
from threading import Thread
from typing import Union

import blessed
from blessed.keyboard import Keystroke

from core.cursor import Player
from core.maze import Maze
from core.render import Render
from core.sound import play_level_up_sound
from game import NEXT_SCENE, QUIT, RESET, Scene
from utils import Boundary

term = blessed.Terminal()
render = Render()


class TitleScene(Scene):
    """Example of a title scene."""

    def __init__(self) -> None:
        super().__init__()
        txt1 = "welcome to 'Game name' :)"
        txt2 = "hit space to start"
        self.current_frame = term.black_on_peachpuff2 + term.clear
        self.current_frame += term.move_xy(
            x=(self.width - len(txt1)) // 2, y=self.height // 2
        )
        self.current_frame += txt1
        self.current_frame += term.move_xy(
            x=(self.width - len(txt1)) // 2, y=self.height // 2 + 1
        )
        self.current_frame += txt2
        self.first_frame = True

    def next_frame(self, val: Keystroke) -> Union[None, int]:
        """Returns next frame to render"""
        # no need to update the frame anymore
        if self.first_frame:
            self.first_frame = False
            render(self.current_frame)
            # return self.current_frame
        elif str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return None
        # return ""

    def reset(self) -> None:
        """Reset has no use for title scene."""
        pass


class Level(Scene):
    """First basic game"""

    def __init__(self, level: str = "1") -> None:
        super().__init__()
        self.maze = Maze.load(level)
        self.level_boundary = Boundary(
            len(self.maze.char_matrix[0]),
            len(self.maze.char_matrix),
            self.maze.top_left_corner,
            term)
        self.player = Player(self.maze.mat2screen(mat=self.maze.start))

        self.end_loc = self.maze.mat2screen(self.maze.end)
        self.first_frame = True
        self.maze_is_visible = False
        for box in self.maze.boxes:
            # move to top-left corner of maze + scale and extend width
            # + move to top-left corner of box
            box.loc = self.maze.top_left_corner + box.loc * (2, 1) - (1, 1)

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame."""
        if self.first_frame:
            self.first_frame = False
            play_level_up_sound()
            # removes the main maze after 2 sec
            Thread(target=self.remove_maze, daemon=True).start()
            frame = term.clear
            frame += self.level_boundary.map
            frame += self.maze.map
            frame += term.move_xy(*self.end_loc) + "&"  # type: ignore
            render(frame)
            for box in self.maze.boxes:
                box.render(self.player)

            self.player.start()

        elif val.is_sequence and (257 < val.code < 262):
            # update player
            self.player.update(val, self.maze)
            # check if game ends
            if all(self.player.avi.coords == self.end_loc):
                return NEXT_SCENE
            # render boxes and mazes
            render(self.level_boundary.map)
            for box in self.maze.boxes:
                box.render(self.player)
            # render player
            render(term.move_xy(*self.end_loc) + "&")
            self.player.render()

        elif val.lower() == "q":
            return QUIT
        elif val.lower() == "r":
            return RESET
        elif val.lower() == "h":
            if not self.maze_is_visible:
                self.maze_is_visible = True
                render(self.maze.map)
                self.player.render()
            else:
                self.maze_is_visible = False
                self.remove_maze(0)
                return ""
        elif val.lower() == "c":
            render(self.maze.erase_map)
            for line in self.maze.char_matrix:
                for c in line:
                    c.render()
        return ""

    def remove_maze(self, sleep: float = 2) -> None:
        """Erase main maze"""
        time.sleep(sleep)
        render(self.maze.erase_map)
        self.player.render()
        for box in self.maze.boxes:
            box.render(self.player)

    def reset(self) -> None:
        """Reset this level"""
        for box in self.maze.boxes:
            box.needs_cleaning = False
        self.player.start()
        self.first_frame = True


class EndScene(Scene):
    """Example of ending scene."""

    def __init__(self):
        super().__init__()
        txt = "You won :o"
        self.current_frame = term.move_xy(
            x=(self.width - len(txt)) // 2, y=self.height // 2
        )
        self.current_frame += txt
        self.first_frame = True

    def next_frame(self, val: Keystroke) -> Union[None, int]:
        """Return next frame to render"""
        # no need to update each frame
        if self.first_frame:
            self.first_frame = False
            render(self.current_frame)
            # return self.render(self.current_frame)
        elif str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return None

    def reset(self) -> None:
        """No use."""
        pass
