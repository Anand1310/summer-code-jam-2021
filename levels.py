"""Examples for designing levels."""
import json
import time
from copy import copy
from threading import Thread
from typing import Dict, Union

import blessed
from blessed.keyboard import Keystroke

from core.maze import Maze
from core.player import Menu, Player
from core.render import Render
from core.sound import enter_game_sound, play_level_up_sound, stop_bgm
from game import (
    CREDITS, LOSE, NEXT_SCENE, PAUSE, PLAY, QUIT, RESET, TITLE, Scene
)
from utils import Boundary, Vec  # type: ignore

term = blessed.Terminal()
render = Render()


class TitleScene(Scene):
    """Example of a title scene."""

    def __init__(self) -> None:
        super().__init__()
        txt = []
        txt.append("welcome to 'Game name' :)")
        txt.append("")
        txt.append("Start")
        txt.append("Credits")
        txt.append("Quit")
        self.current_frame = term.black_on_peachpuff2 + term.clear
        width = (self.width - len(txt[0])) // 2
        height = self.height // 2
        for i in range(len(txt)):
            self.current_frame += term.move_xy(x=width, y=height + i)
            self.current_frame += txt[i]
        self.first_frame = True

        self.menu = Menu(Vec(width - 3, height + 2), Vec(0, 2), txt[2:])

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Returns next frame to render"""
        # no need to update the frame anymore
        if self.first_frame:
            self.first_frame = False
            render(self.current_frame)
            self.menu.render()
            # return self.current_frame
        elif val.is_sequence and (257 < val.code < 262):
            self.menu.move(val.name)
            self.menu.render()
        elif str(val) == " " or val.name == "KEY_ENTER":
            choice = self.menu.options[self.menu.selected]
            if choice == "Start":
                enter_game_sound()
                return NEXT_SCENE
            elif choice == "Credits":
                play_level_up_sound()
                return CREDITS
            else:
                return QUIT
        return ""
        # return ""

    def reset(self) -> None:
        """Reset has no use for title scene."""
        self.first_frame = True
        self.menu.selected = 0
        self.menu.coords = copy(self.menu.l_bounds)


class CreditsScene(Scene):
    """The class for the Credits"""

    def __init__(self) -> None:
        super().__init__()
        txt = []
        txt.append("Credits")
        txt.append("")
        txt.append("Anand")
        txt.append("Pritam Dey")
        txt.append("Jason Ho")
        txt.append("Himi")
        txt.append("Olivia")
        txt.append("Stone Steel")
        txt.append("")
        txt.append("Back")
        self.current_frame = term.black_on_peachpuff2 + term.clear
        width = (self.width - len(txt[0])) // 2
        height = self.height // 4
        for i in range(len(txt)):
            self.current_frame += term.move_xy(x=width, y=height + i)
            self.current_frame += txt[i]
        self.first_frame = True
        self.menu = Menu(Vec(width - 3, height + 2), Vec(0, 7), txt[2:])

    def next_frame(self, val: Keystroke) -> Union[None, int]:
        """Returns next frame to render"""
        # no need to update the frame anymore
        if self.first_frame:
            self.first_frame = False
            render(self.current_frame)
            self.menu.render()
            # return self.current_frame
        elif val.is_sequence and (257 < val.code < 262):
            self.menu.move(val.name)
            self.menu.render()
        elif str(val) == " " or val.name == "KEY_ENTER":
            if self.menu.options[self.menu.selected] == "Back":
                play_level_up_sound()
                return TITLE
        return None

    def reset(self) -> None:
        """Reset this level"""
        self.first_frame = True
        self.menu.selected = 0
        self.menu.coords = copy(self.menu.l_bounds)


class Level(Scene):
    """First basic game"""

    def __init__(self, level: str = "1") -> None:
        super().__init__()

        with open(f"levels/{level}.json", "r") as f:
            data = json.load(f)

        self.instructions: Dict = {}
        self.dialogues = data.pop("dialogues", None)
        if self.dialogues:
            for dialogue in self.dialogues:
                hit_point, coordinate, text = dialogue
                self.instructions[tuple(hit_point)] = [coordinate, text]

        self.maze = Maze.load(data=data)

        self.level_boundary = Boundary(
            len(self.maze.char_matrix[0]),
            len(self.maze.char_matrix),
            self.maze.top_left_corner,
            term,
        )

        self.end_loc = self.maze.end
        self.first_act = True  # set up what to do at the start of the level
        self.show_level = 40  # number of frames to show the level
        self.wait = self.show_level
        self.maze_is_visible = False
        self.reward_on_goal = 0

        self.player: Player = Player()

        for box in self.maze.boxes:
            # move to top-left corner of maze + scale and extend width
            # + move to top-left corner of box
            box.loc = self.maze.mat2screen(box.loc) - (1, 1)
            self.player.inside_box[box.col] = False

    def build_level(self) -> None:
        """Load current level specific attributes"""
        self.player.start_loc = copy(self.maze.start)
        self.player.collision_count = 0
        self.reward_on_goal = 200

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame."""
        if self.first_act:
            self.first_act = False
            self.show_level = 30
            self.build_level()

            play_level_up_sound()
            # show the maze for 1 sec
            frame = term.clear
            frame += self.level_boundary.map
            frame += self.maze.map
            frame += term.move_xy(*self.end_loc) + "&"  # type: ignore
            render(frame)
            for box in self.maze.boxes:
                box.render(self.player)
            self.player.start()
            return ""

        elif self.wait > 0:
            # block any actions from player and then remove maze
            if self.instructions and self.wait == self.show_level:
                Thread(target=self.instruct_player, daemon=True).start()
            self.wait -= 1
            if self.wait == 0:
                self.remove_maze(0)

        elif val.is_sequence and (257 < val.code < 262):
            # update player
            self.player.update(val, self.maze)
            # check if game ends
            if all(self.player.avi.coords == self.end_loc):
                self.player.score.value += self.reward_on_goal
                return NEXT_SCENE
            # render boxes and mazes
            if self.instructions:
                Thread(target=self.instruct_player, daemon=True).start()
            self.render()
        elif val.lower() == "e":
            self.player.player_movement_sound(maze=self.maze)
        elif val.lower() == "q":
            return PAUSE
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

        # things that should update on every frame goes here
        if not self.wait > 0:
            self.player.score.update(
                player_inside_box=any(self.player.inside_box.values())
            )
        if self.player.score.value <= 0:
            return LOSE
        return ""

    def render(self) -> None:
        """Refreshing the scene"""
        for box in self.maze.boxes:
            box.render(self.player)
        render(self.level_boundary.map)
        # render player
        render(term.move_xy(*self.end_loc) + "&")
        self.player.render()

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
        self.first_act = True

    def instruct_player(self) -> None:
        """Instructions"""
        player_loc = tuple(self.maze.screen2mat(self.player.avi.coords))
        if player_loc not in self.instructions.keys():
            return
        coordinate, text = self.instructions.pop(player_loc)
        text_loc = self.maze.mat2screen(coordinate)

        frame = term.move_xy(*text_loc) + text
        render(frame)
        time.sleep(4)
        frame = term.move_xy(*text_loc) + " " * len(text)
        render(frame)


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
            stop_bgm()
            self.first_frame = False
            render(self.current_frame)
            # return self.render(self.current_frame)
        elif str(val) == " " or val.name == "KEY_ENTER":
            return NEXT_SCENE
        return None

    def reset(self) -> None:
        """No use."""
        pass


class Pause(Scene):
    """Pause Screen for the game"""

    def __init__(self):
        super().__init__()
        self.first_frame = True
        self.reset()

    def next_frame(self, val: Keystroke) -> Union[None, int]:
        """Return next frame to render"""
        # no need to update each frame
        if self.first_frame:
            self.first_frame = False
            render(self.current_frame)
        elif val.lower() == "q":
            return QUIT
        elif val.lower() == "p":
            # remove everything from screen
            self.current_frame = term.move_xy(
                x=(self.width - len(self.txt)) // 2, y=self.height // 2
            )
            self.current_frame += " " * len(self.txt)
            self.current_frame += term.move_xy(
                x=(self.width - len(self.txt2)) // 2, y=self.height // 2 + 1
            )
            self.current_frame += " " * len(self.txt2)
            self.current_frame += term.move_xy(
                x=(self.width - len(self.txt3)) // 2, y=self.height
            )
            self.current_frame += " " * len(self.txt3)
            render(self.current_frame)
            return PLAY
        # elif val.lower() == "h":
        #     # help
        # elif val.lower() == "c":
        #     # credits

        return None

    def reset(self) -> None:
        """Reset current scene"""
        self.txt = "This is the pause screen and we need to design it"
        self.txt2 = "Hit p to play"
        self.txt3 = "Hit q again to exit"
        self.current_frame = term.move_xy(
            x=(self.width - len(self.txt)) // 2, y=self.height // 2
        )
        self.current_frame += self.txt
        self.current_frame += term.move_xy(
            x=(self.width - len(self.txt2)) // 2, y=self.height // 2 + 1
        )
        self.current_frame += self.txt2
        self.current_frame += term.move_xy(
            x=(self.width - len(self.txt3)) // 2, y=self.height
        )
        self.current_frame += self.txt3
        self.first_frame = True
