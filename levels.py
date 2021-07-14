"""Examples for designing levels."""
import time
from copy import copy
from threading import Thread
from typing import Union

import blessed
from blessed.keyboard import Keystroke

from core.cursor import Cursor
from core.maze import Maze
from core.render import Render
from core.sound import play_level_up_sound
from game import NEXT_SCENE, QUIT, RESET, Scene
from utils import Vec  # type: ignore

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


class Level_1(Scene):
    """Example of a level."""

    def __init__(self) -> None:
        super().__init__()
        self.first_line = term.clear + "hit 'n' to end the game\n" + term.home
        self.first_frame = True

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Return next frame to render"""
        if self.first_frame:
            self.first_frame = False
            print(self.first_line)
        if not val:
            new_line = ""
        elif val.is_sequence:
            new_line = "got sequence: {0}.".format((str(val), val.name, val.code))
        elif val.lower() == "n":
            return NEXT_SCENE
        elif val.lower() == "q":
            return QUIT
        elif val.lower() == "r":
            return RESET
        elif val:
            new_line = "got {0}.".format(val)

        return new_line

    def reset(self) -> None:
        """Reset the current level"""
        self.first_frame = True


class Level_2(Scene):
    """First basic game"""

    def __init__(self, level: str = "1") -> None:
        super().__init__()
        self.maze = Maze.load(level)

        self.avi = Cursor(
            self.mat2screen(mat=self.maze.start), fill="█", speed=Vec(1, 1)
        )
        self.end_loc = self.mat2screen(self.maze.end)
        self.first_frame = True
        self.maze_is_visible = False
        for box in self.maze.boxes:
            # move to top-left corner of maze + scale and extend width
            # + move to top-left corner of box
            box.loc = self.maze.top_left_corner + box.loc * (2, 1) - (1, 1)

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame"""
        if self.first_frame:
            play_level_up_sound()
            self.first_frame = False
            # removes the main maze after 2 sec
            Thread(target=self.remove_maze, daemon=True).start()
            frame = term.clear
            frame += self.maze.map
            frame += term.move_xy(*self.end_loc) + "&"  # type: ignore
            render(frame)
            for box in self.maze.boxes:
                box.render(self.avi.coords)
            self.avi.render()

        elif val.is_sequence and (257 < val.code < 262):
            avi_loc = self.avi.loc_on_move(val.name)

            if self.wall_at(avi_loc):
                # collision count and music code goes here
                self.avi.hit_wall()
                pass
                # logging.info(f"hit maze @ {avi_loc}")
            elif all(self.avi.coords == self.end_loc):
                return NEXT_SCENE
            else:
                self.avi.move(val.name)
            for box in self.maze.boxes:
                box.render(self.avi.coords)
            self.avi.render()

        elif val.lower() == "q":
            return QUIT
        elif val.lower() == "r":
            return RESET
        elif val.lower() == "h":
            if not self.maze_is_visible:
                self.maze_is_visible = True
                # frame = self.draw_maze(self.maze.draw(), update_cursor=False)  # type: ignore
                # frame += self.avi.render()  # type: ignore
                self.draw_maze(self.maze.map, update_cursor=False)  # type: ignore
                self.avi.render()  # type: ignore
                # return frame
            else:
                self.maze_is_visible = False
                self.remove_maze(0)
                return ""
        return ""

    def draw_maze(self, maze: str, update_cursor: bool = True) -> None:
        """Draw main maze"""
        if update_cursor:
            self.avi.coords = self.maze.top_left_corner + self.maze.start * (2, 1)
        frame = term.move_xy(*self.maze.top_left_corner) + maze
        render(frame)
        # return

    def remove_maze(self, sleep: float = 2) -> None:
        """Erase main maze"""
        time.sleep(sleep)
        maze = self.maze.map
        for chr in "┼├┴┬┌└─╶┤│┘┐╷╵╴":
            if chr in maze:
                maze = maze.replace(chr, " ")
        self.draw_maze(maze, update_cursor=False)  # erase maze
        # frame = self.draw_maze(maze, update_cursor=False)  # erase maze
        # frame += self.avi.render()  # draw avi
        self.avi.render()  # draw avi
        for box in self.maze.boxes:
            box.render(self.avi.coords)

    def wall_at(self, screen: Vec) -> bool:
        """Return True if there is a wall at (x, y). Values outside the valid range always return False."""
        x, y = self.screen2mat(screen)
        screen = screen - self.maze.top_left_corner
        # logging.info(
        #     f"{x=}\t{screen.x=}\t{self.maze.matrix[y][x]}, {self.maze.matrix[y][x-1]}, {self.maze.matrix[y][x+1]}"
        # )
        if 0 <= x < len(self.maze.matrix[0]) and 0 <= y < len(self.maze.matrix):
            is_wall = self.maze.matrix[y][x] == 1
            # if is_wall and screen.x == 2 * x + 1:
            #     return False
            # else:
            #     return True
            return is_wall
        else:
            return False

    def screen2mat(self, screen: Vec) -> Vec:
        """Convert screen location of a point to matrix location"""
        return (screen - self.maze.top_left_corner) // (2, 1)

    def mat2screen(self, mat: Vec) -> Vec:
        """Convert matrix location of a point to screen location"""
        return self.maze.top_left_corner + mat * (2, 1)

    def reset(self) -> None:
        """Reset this level"""
        for box in self.maze.boxes:
            box.needs_cleaning = False
        self.avi.coords = copy(self.maze.start)
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
