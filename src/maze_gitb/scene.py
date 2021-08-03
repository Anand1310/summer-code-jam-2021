"""Examples for designing levels."""
import json
import logging
import os
import time
from copy import copy
from random import randrange
from threading import Thread
from typing import Callable, Dict, List, Union

import blessed
from blessed.keyboard import Keystroke

from maze_gitb.core.maze import AIR, Box, Maze
from maze_gitb.core.player import MenuCursor, Player
from maze_gitb.core.render import Render
from maze_gitb.core.sound import (
    enter_game_sound, play_level_up_sound, stop_bgm
)
from maze_gitb.core.table import make_table
from maze_gitb.game import (
    CREDITS, END, INFINITE, LEADERBOARD, LOSE, NEXT_SCENE, PAUSE, PLAY, QUIT,
    RESET, TITLE, TUTORIAL, Scene
)
from maze_gitb.utils import Boundary, Vec  # type: ignore

term = blessed.Terminal()
render = Render()


class Menu(Scene):
    """Example of a title scene."""

    def __init__(
        self,
        txt: List[str],
        choices: List[str],
        action_on_choice: Callable,
        action_on_first_frame: Callable = None,
    ) -> None:
        super().__init__()
        self.txt = txt
        self.choices = choices
        self.init_choices = choices
        self.built_once = False
        self.action_on_choice = action_on_choice
        self.action_on_first_frame = action_on_first_frame

        self.first_frame = True
        self.current_frame: str = ""
        self.menu: MenuCursor = None

    def build(self) -> None:
        """Build self.txt"""
        if self.action_on_first_frame and not self.built_once:
            self.built_once = True
            self.choices = ""
            self.choices = self.action_on_first_frame() + self.init_choices
        self.current_frame = term.black_on_peachpuff2 + term.clear
        width = (self.width - max(len(s) for s in self.txt)) // 2
        txt = self.txt + list(self.choices)
        height = self.height // 2 - len(txt) // 2
        for i in range(len(txt)):
            self.current_frame += term.move_xy(x=width, y=height + i)
            self.current_frame += txt[i]

        self.menu = MenuCursor(
            Vec(width - 3, height + 2),
            Vec(0, len(self.choices) - 1),
            list(self.choices),
        )

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Returns next frame to render"""
        # no need to update the frame anymore
        if self.first_frame:
            self.build()
            self.first_frame = False
            render(self.current_frame)
            self.menu.render()
            # return self.current_frame
        elif val.is_sequence and (257 < val.code < 262):
            self.menu.move(val.name)
            self.menu.render()
        elif str(val) == " " or val.name == "KEY_ENTER":
            choose = 0
            if self.menu.selected > len(self.menu.options):
                choose = len(self.menu.options) - 1
            else:
                choose = self.menu.selected
            choice = self.menu.options[choose]

            play_level_up_sound()
            return self.action_on_choice(choice)
        return ""
        # return ""

    def reset(self) -> None:
        """Reset has no use for title scene."""
        self.first_frame = True
        self.menu.selected = 0
        self.menu.coords = copy(self.menu.l_bounds)


dirname = os.path.dirname(__file__)


class Level(Scene):
    """First basic game"""

    def __init__(self, level: str = "1") -> None:
        super().__init__()

        with open(os.path.join(dirname, f"levels/{level}.json"), "r") as f:
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
            # removes the main maze after 2 sec
            frame = self.get_boundary_frame()  # type: ignore
            frame += self.maze.map
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
                for box in self.maze.boxes:
                    box.render(self.player)
                self.player.render()
            else:
                self.remove_maze(0)

        # things that should update on every frame goes here
        if not self.wait > 0:
            self.player.score.update(
                player_inside_box=any(self.player.inside_box.values())
            )
        if self.player.score.value <= 0:
            return LOSE
        return ""

    def render(self, hard: bool = False) -> None:
        """Refreshing the scene"""
        if hard:
            render(term.clear, bg_col="lightskyblue1")
        for box in self.maze.boxes:
            box.render(self.player)
        render(self.level_boundary.map)
        # render player
        render(term.move_xy(*self.end_loc) + "&")
        self.player.render()

    def remove_maze(self, sleep: float = 2) -> None:
        """Erase main maze"""
        self.maze_is_visible = False
        time.sleep(sleep)
        render(self.get_boundary_frame())
        self.player.render()
        for box in self.maze.boxes:
            box.render(self.player)

    def get_boundary_frame(self) -> str:
        """Get the frame with only boundary"""
        frame = term.clear
        frame += self.level_boundary.map
        frame += term.move_xy(*self.end_loc) + "&"  # type: ignore
        return frame

    def reset(self) -> None:
        """Reset this level"""
        for box in self.maze.boxes:
            box.needs_cleaning = False
        self.player.start()
        self.first_act = True

    global prev_text, prev_text_loc
    prev_text, prev_text_loc = "", ""

    def instruct_player(self) -> None:
        """Instructions"""
        global prev_text, prev_text_loc
        player_loc = tuple(self.maze.screen2mat(self.player.avi.coords))
        if player_loc not in self.instructions.keys():
            return
        if prev_text != "":
            frame = term.move_xy(*prev_text_loc) + " " * len(prev_text)
            render(frame)
        coordinate, text = self.instructions.pop(player_loc)
        text_loc = self.maze.mat2screen(coordinate)
        frame = term.move_xy(*text_loc) + text
        render(frame)
        prev_text = text
        prev_text_loc = text_loc
        # time.sleep(2)
        # frame = term.move_xy(*text_loc) + " " * len(text)
        # render(frame)

        # time.sleep(4)
        # frame = term.move_xy(*text_loc) + " " * len(text)
        # render(frame)


class InfiniteLevel(Scene):
    """Infinite level of maze"""

    instance = None
    random = None

    def __init__(self, random_pos: bool) -> None:
        global random
        super().__init__()
        self.player: Player = Player()
        if type(self).instance is None:
            self.maze = Maze.generate(term.width // 5, term.height // 3, random_pos=random_pos)
            random = random_pos
            # self.maze = Maze.generate(7, 7, random_pos=random_pos)
            self.generate_boxes()
            self.level_boundary = Boundary(
                len(self.maze.char_matrix[0]),
                len(self.maze.char_matrix),
                self.maze.top_left_corner,
                term,
            )
            self.end_loc = self.maze.mat2screen(self.maze.end)
            self.first_act = True  # set up what to do at the start of the level
            self.show_level = 40  # number of frames to show the level
            self.wait = self.show_level
            self.maze_is_visible = False
            self.reward_on_goal = 0

            for box in self.maze.boxes:
                # move to top-left corner of maze + scale and extend width
                # + move to top-left corner of box
                box.loc = self.maze.mat2screen(box.loc) - (1, 1)
                self.player.inside_box[box.col] = False

            type(self).instance = self
        else:
            logging.error(
                RuntimeError("Only one instance of 'Infinitelevel' can exist at a time")
            )

    def build_level(self) -> None:
        """Load current level specific attributes"""
        self.player.start_loc = self.maze.mat2screen(mat=self.instance.maze.start)
        self.player.collision_count = 0
        self.instance.reward_on_goal = self.instance.maze.width * self.instance.maze.height

    def next_frame(self, val: Keystroke) -> Union[str, int]:
        """Draw next frame."""
        if self.instance.first_act:
            self.instance.first_act = False
            time = self.maze.width * self.maze.height // 6.7
            self.instance.show_level = time if time > 30 else 30
            self.instance.wait = self.instance.show_level
            self.build_level()

            play_level_up_sound()
            # removes the main maze after 2 sec
            frame = self.get_boundary_frame()
            frame += self.instance.maze.map
            render(frame)
            for box in self.instance.maze.boxes:
                box.render(self.player)
            self.player.start()
            return ""

        elif self.instance.wait > 0:
            # block any actions from player and then remove maze
            self.instance.wait -= 1
            if self.instance.wait == 0:
                self.remove_maze(0)

        elif val.is_sequence and (257 < val.code < 262):
            # update player
            self.player.update(val, self.instance.maze)
            # check if game ends
            if all(self.player.avi.coords == self.instance.end_loc):
                self.player.score.value += self.instance.reward_on_goal
                self.instance.reset_cls()
                self.instance.next_frame(Keystroke())
                return
            self.render()
        elif val.lower() == "e":
            self.player.player_movement_sound(maze=self.maze)
        elif val.lower() == "q":
            self.instance.reset_cls()
            self.player.score.value -= self.instance.reward_on_goal
            self.reset()
            return END
        elif val.lower() == "r":
            return RESET
        elif val.lower() == "h":
            if not self.instance.maze_is_visible:
                self.instance.maze_is_visible = True
                render(self.instance.maze.map)
                for box in self.instance.maze.boxes:
                    box.render(self.player)
                render(term.move_xy(*self.instance.end_loc) + "&")
                self.instance.player.render()
            else:
                self.instance.remove_maze(0)

        # things that should update on every frame goes here
        if not self.instance.wait > 0:
            self.player.score.update(
                player_inside_box=any(self.player.inside_box.values())
            )
        if self.player.score.value <= 0:
            return LOSE
        return ""

    def render(self, hard: bool = False) -> None:
        """Refreshing the scene"""
        if hard:
            render(term.clear, bg_col="lightskyblue1")
        for box in self.instance.maze.boxes:
            box.render(self.player)
        render(self.instance.level_boundary.map)
        # render player
        render(term.move_xy(*self.instance.end_loc) + "&")
        self.player.render()

    def remove_maze(self, sleep: float = 2) -> None:
        """Erase main maze"""
        self.instance.maze_is_visible = False
        time.sleep(sleep)
        render(self.get_boundary_frame())
        for box in self.instance.maze.boxes:
            box.render(self.player)
        self.player.render()

    def get_boundary_frame(self) -> str:
        """Get the frame with only boundary"""
        frame = term.clear
        frame += self.instance.level_boundary.map
        frame += term.move_xy(*self.instance.end_loc) + "&"  # type: ignore
        return frame

    def generate_boxes(self) -> None:
        """Generate boxes"""
        num_box_x = self.maze.width // 6
        num_box_y = self.maze.height // 4
        if num_box_y == 0:
            num_box_y = 1
        if num_box_x == 0:
            num_box_x = 1
        radius = (
            max(self.maze.width * 2 // num_box_x, self.maze.height // num_box_y) + 3
        )
        number_of_box = num_box_x * num_box_y
        box_list = []
        logging.debug("radius {}".format(radius))
        logging.debug("width:" + str(self.maze.width))
        logging.debug("height:" + str(self.maze.height))
        logging.debug("number of box:" + str(number_of_box))
        logging.debug("\n" + str(self.maze))
        for y in range(0, num_box_y):
            for x in range(0, num_box_x):
                box_pos = None
                while (
                    box_pos is None
                    or box_pos.x < 2
                    or box_pos.y < 2
                    or box_pos.y > len(self.maze.matrix[1]) - 2
                    or box_pos.x > len(self.maze.matrix) - 2
                    or self.maze.matrix[box_pos.x][box_pos.y] != AIR
                    or all(box_pos == self.maze.start)
                    or all(box_pos == self.maze.end)
                ):
                    box_pos = Vec(
                        self.maze.height // num_box_y // 2
                        + (self.maze.height * 2 // num_box_y) * y
                        + randrange(-2, 2),
                        self.maze.width * 2 // num_box_x // 2
                        + (self.maze.width * 2 // num_box_x) * x
                        + randrange(-2, 2))
                logging.debug("Box pos: {}".format(str(box_pos)))
                box = Box(box_pos)
                box.generate_map(self.maze, radius)
                box.generate_image()
                box_list.append(box)
        self.maze.boxes = box_list

    def reset(self) -> None:
        """Reset this level"""
        for box in self.instance.maze.boxes:
            box.needs_cleaning = False
        self.player.start_loc = self.instance.maze.mat2screen(mat=self.maze.start)
        self.player.start()
        self.instance.first_act = True

    @classmethod
    def reset_cls(cls):
        """Reset class"""
        global random
        cls.instance = None
        cls.instance = InfiniteLevel(random)


class EndScene(Scene):
    """Example of ending scene."""

    def __init__(self):
        super().__init__()
        self.set_init_frame()
        self.first_frame = True
        self.name = ""
        self.player: Player = Player()

    def set_player(self, player: Player) -> None:
        """Set player for getting their name after game is over."""
        self.player = player

    def set_init_frame(self) -> None:
        """Set current frame to init frame."""
        txt = "You won, what shall you be remembered as?"
        txt2 = "Press enter when you've decided your name."
        txt3 = "Press escape if you don't want to be remembered."
        self.current_frame = term.clear + term.move_xy(
            x=(self.width - len(txt)) // 2, y=self.height // 2
        )
        self.current_frame += txt
        self.current_frame += term.move_xy(
            x=(self.width - len(txt2)) // 2, y=self.height // 2 + 4
        )
        self.current_frame += txt2
        self.current_frame += term.move_xy(
            x=(self.width - len(txt3)) // 2, y=self.height - 5
        )
        self.current_frame += txt3

    def next_frame(self, val: Keystroke) -> Union[None, int]:
        """Return next frame to render."""
        if self.first_frame:
            stop_bgm()
            self.first_frame = False
            render(self.current_frame)
            # return self.render(self.current_frame)
        elif val.lower() == "q":
            return QUIT
        else:
            inp = term.inkey()
            if inp.code == term.KEY_ENTER:
                # save score
                with open(os.path.join(dirname, "leaderboard.txt"), "a") as score_file:
                    score_file.write(f"{self.name}>{self.player.score.value:.2f}\n")

                score_file.close()
                return LEADERBOARD
            elif inp.code == term.KEY_ESCAPE or inp == chr(3):
                # don't save score
                self.set_init_frame()
                return LEADERBOARD
            elif (not inp.is_sequence and len(self.name) < 50 and inp != ">"
                    and not (len(self.name) == 0 and inp == " ")):
                self.name += inp
            elif inp.code in (term.KEY_BACKSPACE, term.KEY_DELETE):
                self.name = self.name[:-1]
                self.current_frame += term.move_left(1)
                self.current_frame += " "
            if self.name:
                self.current_frame += term.move_xy(
                    x=self.width // 2, y=self.height // 2 + 1
                )
                self.current_frame += term.bold + self.name + term.normal
            render(self.current_frame)

    def reset(self) -> None:
        """No use."""
        pass


class Pause(Scene):
    """Pause Screen for the game."""

    def __init__(self):
        super().__init__()
        self.txt = "PAUSED"
        self.txt2 = "Hit p to play"
        self.txt3 = "Hit q again to exit"
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
        self.current_frame = term.clear + term.move_xy(
            x=(self.width - len(self.txt)) // 2, y=self.height // 2
        )
        self.current_frame += term.bold + self.txt + term.normal
        self.current_frame += term.move_xy(
            x=(self.width - len(self.txt2)) // 2, y=self.height // 2 + 1
        )
        self.current_frame += self.txt2
        self.current_frame += term.move_xy(
            x=(self.width - len(self.txt3)) // 2, y=self.height - 5
        )
        self.current_frame += self.txt3
        self.first_frame = True


class Leaderboard(Scene):
    """Example of a title scene.

    Not used
    """

    def __init__(self) -> None:
        super().__init__()
        txt1 = "Your name has been etched onto the sands of time."
        self.current_frame = term.firebrick_on_lightgreen + term.clear
        self.current_frame += term.move_xy(x=(self.width - len(txt1)) // 2, y=3)
        self.current_frame += txt1

        self.first_frame = True

    def next_frame(self, val: Keystroke) -> Union[None, int]:
        """Returns next frame to render"""
        # no need to update the frame anymore
        if self.first_frame:
            self.first_frame = False
            with open("leaderboard.txt", "r") as f:
                players = f.read()
                players_sorted = sorted(
                    [player.split(">") for player in players.split("\n")[:-1]],
                    key=lambda x: float(x[1]),
                    reverse=True,
                )
                scores = make_table(
                    rows=players_sorted,
                    labels=["Name", "Persistence"],
                    centered=True,
                )

                table_width = len(scores.split("\n")[0])
                for n, line in enumerate(scores.split("\n")):
                    self.current_frame += term.move_xy(
                        x=(self.width - table_width) // 2,
                        y=n + 5,
                    )
                    self.current_frame += line
            render(self.current_frame)
            # return self.current_frame
        elif str(val) == " " or val.name == "KEY_ENTER":
            return END
        return None
        # return ""

    def reset(self) -> None:
        """Reset has no use for title scene."""


def title_menu_action(choice: str) -> Union[int, None]:
    """Actions for Title menu"""
    logging.info("title")
    if choice == "Start":
        enter_game_sound()
        return NEXT_SCENE
    elif choice == "Infinite":
        enter_game_sound()
        return INFINITE
    elif choice == "Credits":
        return CREDITS
    elif choice == "Tutorial":
        enter_game_sound()
        return TUTORIAL
    elif choice == "Leaderboard":
        return LEADERBOARD
    else:
        return QUIT


title_scene = Menu(
    txt=["Welcome :)", ""],
    choices=["Start", "Infinite", "Tutorial", "Credits", "Leaderboard", "Quit"],
    action_on_choice=title_menu_action,
)


def credit_menu_action(choice: str) -> Union[int, None]:
    """Actions for Credit menu"""
    logging.info("credit")
    if choice == "Back":
        return TITLE
    return None


credit_scene = Menu(
    txt=["Creidts", ""],
    choices=[
        "Anand",
        "Pritam Dey",
        "Jason Ho",
        "Himi",
        "Olivia",
        "StoneSteel",
        "",
        "Back",
    ],
    action_on_choice=credit_menu_action,
)


def pause_menu_action(choice: str) -> Union[int, None]:
    """Actions for Pause menu"""
    if choice == "Return":
        return PLAY
    elif choice == "Quit":
        return QUIT
    elif choice == "Main menu":
        return TITLE
    return None


pause_menu = Menu(
    txt=["Game Paused", ""],
    choices=["Return", "Main menu", "Quit"],
    action_on_choice=pause_menu_action,
)


def leaderboard_action(choice: str) -> Union[None, int]:
    """Action for leaderboard"""
    if choice == "Main Menu":
        return TITLE
    return None


def leaderboard_first_frame() -> List[str]:
    """First frame action for leaderboard"""
    with open(os.path.join(dirname, "leaderboard.txt"), "r") as f:
        players = f.read()
        players_sorted = sorted(
            [player.split(">") for player in players.split("\n")[:-1]],
            key=lambda x: float(x[1]),
            reverse=True,
        )
    players_sorted = ["\t".join(player) for player in players_sorted]
    if len(players_sorted) > 10:
        players_sorted = players_sorted[:10]
    return players_sorted


leaderboard_menu = Menu(
    txt=["Leaderboard", ""],
    choices=["Main Menu"],
    action_on_choice=leaderboard_action,
    action_on_first_frame=leaderboard_first_frame,
)
