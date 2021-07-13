from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path
from threading import Thread
from typing import Callable, Dict, Iterator, List, Tuple

import blessed
import numpy as np

from game import Cursor
from utils import Vec  # type: ignore

# from pprint import pprint


# Easy to read representation for each cardinal direction.
N, S, W, E = ("n", "s", "w", "e")
TARGET = 4
PLAYER = 3
AIR = 0

term = blessed.Terminal()


class Cell(object):
    """Class for each individual cell. Knows only its position and which walls are still standing."""

    def __init__(self, x: int, y: int, walls: list):
        self.x = x
        self.y = y
        self.walls = set(walls)

    def __repr__(self):
        # <15, 25 (es  )>
        return "<{}, {} ({:4})>".format(self.x, self.y, "".join(sorted(self.walls)))

    def __contains__(self, item: object) -> bool:
        # N in cell
        return item in self.walls

    def is_full(self) -> bool:
        """Returns True if all walls are still standing."""
        return len(self.walls) == 4

    def _wall_to(self, other: Cell) -> str:
        """
        Returns the direction to the given cell from the current one.

        Must be one cell away only.
        """
        if other.y < self.y:
            return N
        elif other.y > self.y:
            return S
        elif other.x < self.x:
            return W
        elif other.x > self.x:
            return E
        else:
            return None

    def connect(self, other: Cell) -> None:
        """Removes the wall between two adjacent cells."""
        other.walls.remove(other._wall_to(self))
        self.walls.remove(self._wall_to(other))


class Maze(object):
    """Maze class containing full board and maze generation algorithms."""

    # Unicode character for a wall with other walls in the given directions.
    UNICODE_BY_CONNECTIONS = {
        "ensw": "┼",
        "ens": "├",
        "enw": "┴",
        "esw": "┬",
        "es": "┌",
        "en": "└",
        "ew": "─",
        "e": "╶",
        "nsw": "┤",
        "ns": "│",
        "nw": "┘",
        "sw": "┐",
        "s": "╷",
        "n": "╵",
        "w": "╴",
    }

    def __init__(self, width: int = 20, height: int = 10):
        """Creates a new maze with the given sizes, with all walls standing."""
        self.width = width
        self.height = height
        self.cells = []
        for y in range(self.height):
            for x in range(self.width):
                self.cells.append(Cell(x, y, [N, S, E, W]))
        self.matrix = self.to_list_matrix()
        self.boxes: List[Box] = []
        self.start: Vec = None
        self.end: Vec = None
        self.min_distance = np.sqrt(self.height ^ 2 + self.width ^ 2)

    def __getitem__(self, index: Tuple[int, int]):
        """Returns the cell at index = (x, y)."""
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x + y * self.width]
        else:
            return None

    def neighbors(self, cell: Cell) -> Iterator[Cell]:
        """
        Returns the list of neighboring cells, not counting diagonals.

        Cells on borders or corners may have less than 4 neighbors.
        """
        x = cell.x
        y = cell.y
        for new_x, new_y in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]:
            neighbor = self[new_x, new_y]
            if neighbor is not None:
                yield neighbor

    def to_list_matrix(self) -> np.ndarray:
        """Returns a matrix with a pretty printed visual representation of this maze."""
        str_matrix = np.array(
            [[1] * (self.width * 2 + 1) for i in range(self.height * 2 + 1)]
        )
        for cell in self.cells:
            x = cell.x * 2 + 1
            y = cell.y * 2 + 1
            str_matrix[y][x] = 0
            if N not in cell and y > 0:
                str_matrix[y - 1][x + 0] = 0
            if S not in cell and y + 1 < self.width:
                str_matrix[y + 1][x + 0] = 0
            if W not in cell and x > 0:
                str_matrix[y][x - 1] = 0
            if E not in cell and x + 1 < self.width:
                str_matrix[y][x + 1] = 0

        self.matrix = str_matrix
        return str_matrix

    def wall_at(self, x: int, y: int) -> bool:
        """Return True if there is a wall at (x, y). Values outside the valid range always return False."""
        # Starts with regular representation. Looks stretched because chars are
        # twice as high as they are wide (look at docs example in
        # `Maze._to_str_matrix`).
        skinny_matrix = self.matrix

        # Simply duplicate each character in each line.
        double_wide_matrix = []
        for line in skinny_matrix:
            double_wide_matrix.append([])
            for item in line:
                char = "O" if item == 1 else " "
                double_wide_matrix[-1].append(char)
                double_wide_matrix[-1].append(char)

        # The last two chars of each line are walls, and we will need only one.
        # So we remove the last char of each line.
        matrix = [line[:-1] for line in double_wide_matrix]

        if 0 <= x < len(matrix[0]) and 0 <= y < len(matrix):
            return matrix[y][x] != " "
        else:
            return False

    def __repr__(self):
        """
        Returns an Unicode representation of the maze. Size is doubled horizontally to avoid a stretched look.

        Example 5x5:
        ┌───┬───────┬───────┐
        │   │       │       │
        │   │   ╷   ╵   ╷   │
        │   │   │       │   │
        │   │   └───┬───┘   │
        │   │       │       │
        │   └───────┤   ┌───┤
        │           │   │   │
        │   ╷   ╶───┘   ╵   │
        │   │               │
        └───┴───────────────┘
        """
        # Starts with regular representation. Looks stretched because chars are
        # twice as high as they are wide (look at docs example in
        # `Maze._to_str_matrix`).
        skinny_matrix = self.matrix

        # Simply duplicate each character in each line.
        double_wide_matrix = []
        for line in skinny_matrix:
            double_wide_matrix.append([])
            for item in line:
                char = "O" if item == 1 else " "
                double_wide_matrix[-1].append(char)
                double_wide_matrix[-1].append(char)

        # The last two chars of each line are walls, and we will need only one.
        # So we remove the last char of each line.
        matrix = [line[:-1] for line in double_wide_matrix]

        def wall_at(x: int, y: int) -> bool:
            """Return True if there is a wall at (x, y). Values outside the valid range always return False."""
            if 0 <= x < len(matrix[0]) and 0 <= y < len(matrix):
                return matrix[y][x] != " "
            else:
                return False

        # Fix double wide walls, finally giving the impression of a symmetric
        # maze.
        for y, line in enumerate(matrix):
            for x, char in enumerate(line):
                if not wall_at(x, y) and wall_at(x - 1, y):
                    matrix[y][x - 1] = " "

        # Right now the maze has the correct aspect ratio, but is still using
        # 'O' to represent walls.

        # Finally we replace the walls with Unicode characters depending on
        # their context.
        for y, line in enumerate(matrix):
            for x, char in enumerate(line):
                if not wall_at(x, y):
                    continue

                connections = {N, S, E, W}
                if not wall_at(x, y + 1):
                    connections.remove(S)
                if not wall_at(x, y - 1):
                    connections.remove(N)
                if not wall_at(x + 1, y):
                    connections.remove(E)
                if not wall_at(x - 1, y):
                    connections.remove(W)

                str_connections = "".join(sorted(connections))
                # Note we are changing the matrix we are reading. We need to be
                # careful as to not break the `g` function implementation.
                matrix[y][x] = Maze.UNICODE_BY_CONNECTIONS[str_connections]

        # Simple double join to transform list of lists into string.
        return "\n".join("".join(line) for line in matrix) + "\n"

    def randomize(self) -> None:
        """
        Knocks down random walls to build a random perfect maze.

        Algorithm from http://mazeworks.com/mazegen/mazetut/index.htm
        (The website is currently down)
        """
        cell_stack = []
        cell = random.choice(self.cells)
        n_visited_cells = 1

        while n_visited_cells < len(self.cells):
            neighbors = [c for c in self.neighbors(cell) if c.is_full()]
            if len(neighbors):
                neighbor = random.choice(neighbors)
                cell.connect(neighbor)
                cell_stack.append(cell)
                cell = neighbor
                n_visited_cells += 1
            else:
                cell = cell_stack.pop()
        self.matrix = self.to_list_matrix()

    def _get_random_position(self) -> Tuple[int, int]:
        """Returns a random position on the maze."""
        return Vec(random.randrange(0, self.width), random.randrange(0, self.height))

    def get_random_start_end_position(self, random_pos: bool = False) -> None:
        """Return a array with start and end position"""

        def check() -> bool:
            """Return whether the player and target location are valid"""
            if self.start is None and all(self.start == self.end) and self.end is None:
                return False
            else:
                distance = sum(np.sqrt(self.start ^ 2 + self.end ^ 2))
                if distance < self.min_distance:
                    return False
                return True

        if random_pos:
            while not check():
                self.start = self._get_random_position()
                self.end = self._get_random_position()
        else:
            while (
                self.start is None or self.matrix[self.start[0]][self.start[1]] != AIR
            ):
                self.start = Vec(random.randrange(0, self.height), 1)
            while self.end is None or self.matrix[self.end[0]][self.end[1]] != AIR:
                self.end = Vec(random.randrange(0, self.height), self.width * 2 - 1)

    def draw(self) -> str:
        """Draw maze on screen"""
        maze = str(self).split("\n")  # type: ignore
        maze_shape = Vec(len(maze[0]), len(maze))
        new_line = term.move_left(maze_shape.x) + term.move_down(1)
        maze = new_line.join(maze)  # type: ignore
        maze = maze.replace(" ", term.move_right(1))  # type: ignore
        return maze  # type: ignore

    @classmethod
    def generate(cls, width: int = 20, height: int = 10):
        """Returns a new random perfect maze with the given sizes."""
        m = cls(width, height)
        m.randomize()
        return m

    def set_map(self, m: List[List[int]]) -> None:
        """Set map for the maze"""
        self.matrix = np.array(m)
        self.width = self.matrix.shape[0] // 2
        self.height = self.matrix.shape[1] // 2

    @classmethod
    def load(cls, fname: str) -> Maze:
        """Load everything from json file"""
        obj = cls(width=20, height=10)
        with open(f"levels/{fname}.json", "r") as f:
            data: Dict = json.load(f)
        obj.set_map(data.pop("map"))
        obj.start = Vec(*reversed(data.pop("start")))
        obj.end = Vec(*reversed(data.pop("end")))
        for color, box_dict in data.items():
            box_location = Vec(*reversed(box_dict["location"]))
            box_map = box_dict["map"]
            box_maze = cls(width=20, height=10)
            box_maze.set_map(box_map)
            obj.boxes.append(Box(location=box_location, maze=box_maze, col=color))

        return obj

    def save_to_file(self) -> str:
        """Save maze in to file

        :parm secure: True -> use pickle to store, False -> use normal method
        """
        maze_count = 0
        map_dir = Path("maps")
        if map_dir not in os.listdir():
            os.mkdir("maps")
        for i in os.listdir("maps"):
            if i.startswith("maze"):
                maze_count += 1
        map_name = "maze" + str(maze_count + 1)
        file_path = map_dir.joinpath(map_name)
        os.mkdir(file_path)

        np.save(str(file_path.joinpath("data")), self.matrix)

        self.get_random_start_end_position()

        # data = {"start": [self.player], "end": [self.target]}

        return map_name


class Box:
    """Box where parts of maze become visible."""

    def __init__(
        self,
        location: Vec,
        maze: Maze,
        shape: Vec = Vec(3, 3),
        col: str = "black",
        render: Callable = None,
    ):
        self.maze = maze
        self.shape = shape
        self.col = col
        self.scene_render = render
        self.top_left_corner: Vec = None
        self.needs_cleaning: bool = False

        self._loc = location
        self.b = (self._loc + (shape.x, 0)) - (1, 0)
        self.c = self.b + (0, shape.y)

    @property
    def loc(self) -> Vec:
        """Return self location"""
        return self._loc

    @loc.setter
    def loc(self, val: Vec) -> None:
        self._loc = val
        self.b = self._loc + (self.shape.x, 0)
        self.c = self.b + (0, self.shape.y)

    def render(self, avi: Cursor) -> str:
        """Draw self"""
        move = term.move_xy(*self.loc)
        # frame = "┌" + "─" * (self.shape.x - 2) + "┐"
        frame = move + "┌" + " " * (self.shape.x - 2) + "┐"
        frame += term.move_down(self.shape.y - 1)
        frame += term.move_left(self.shape.x)
        # frame += "└" + "─" * (self.shape.x - 2) + "┘"
        frame += "└" + " " * (self.shape.x - 2) + "┘"  # box drawing
        frame += term.move_xy(*self.top_left_corner)
        frame += self.show_maze(avi)
        return self.scene_render(frame, col=self.col)

    def show_maze(self, avi: Cursor) -> str:
        """Return a string that draws the box and associated maze based on player location."""
        player_inside_box = False

        for i in range(1, self.shape.x - 1):
            for j in range(1, self.shape.y - 1):
                p = self._loc + (i, j)
                player_inside_box = all(avi.coords == p)
                if player_inside_box:
                    break
            if player_inside_box:
                break

        # AB = self.b - self.loc
        # BC = self.c - self.b

        # proj_AB = np.dot(AB, player_location - self.loc)
        # proj_BC = np.dot(BC, player_location - self.b)

        # https://stackoverflow.com/a/2763387
        # if (0 <= proj_AB <= np.dot(AB, AB)) and (0 <= proj_BC <= np.dot(BC, BC)):
        if player_inside_box:
            Thread(target=avi.enter_box, daemon=True).start()
            self.needs_cleaning = True
            frame = self.maze.draw()
            return frame
        elif self.needs_cleaning:
            self.needs_cleaning = False
            frame = self.maze.draw()
            for chr in "┼├┴┬┌└─╶┤│┘┐╷╵╴":
                if chr in frame:
                    frame = frame.replace(chr, " ")
            return frame
        else:
            return ""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        width = int(sys.argv[1])
        if len(sys.argv) > 2:
            height = int(sys.argv[2])
        else:
            height = width
    else:
        width = 20
        height = 10

    maze = Maze.generate(width, height)
    print(maze)
    for i in maze.get_matrix_with_start_end_position():
        for q in i:
            print(q, end="")
        print()
    # maze.save_to_file()
    # print(np.load("maps/maze1/data.npy", allow_pickle=False))
