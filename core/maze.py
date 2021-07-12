import os
import random
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np

from utils import calc_distance

N, S, W, E = ("n", "s", "w", "e")
TARGET = '$'
PLAYER = 'ጿ'
WALL = 'W'


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

    def _wall_to(self, other: object) -> str:
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

    def connect(self, other: List[object]) -> None:
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
        self.player, self.target = None, None
        self.min_distance = calc_distance((self.height, 0), (self.width, 0))

    def __getitem__(self, index: set):
        """Returns the cell at index = (x, y)."""
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x + y * self.width]
        else:
            return None

    def neighbors(self, cell: Cell) -> list:
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
        str_matrix = np.array([[WALL] * (self.width * 2 + 1) for i in range(self.height * 2 + 1)])
        for cell in self.cells:
            x = cell.x * 2 + 1
            y = cell.y * 2 + 1
            str_matrix[y][x] = " "
            if N not in cell and y > 0:
                str_matrix[y - 1][x + 0] = " "
            if S not in cell and y + 1 < self.width:
                str_matrix[y + 1][x + 0] = " "
            if W not in cell and x > 0:
                str_matrix[y][x - 1] = " "
            if E not in cell and x + 1 < self.width:
                str_matrix[y][x + 1] = " "

        self.matrix = str_matrix
        return str_matrix

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
        skinny_matrix = self.to_list_matrix()

        # Simply duplicate each character in each line.
        double_wide_matrix = []
        for line in skinny_matrix:
            double_wide_matrix.append([])
            for char in line:
                double_wide_matrix[-1].append(char)
                double_wide_matrix[-1].append(char)

        # The last two chars of each line are walls, and we will need only one.
        # So we remove the last char of each line.
        matrix = [line[:-1] for line in double_wide_matrix]

        def g(x: int, y: int) -> bool:
            """Returns True if there is a wall at (x, y). Values outside the valid range always return false."""
            if 0 <= x < len(matrix[0]) and 0 <= y < len(matrix):
                return matrix[y][x] != " "
            else:
                return False

        # Fix double wide walls, finally giving the impression of a symmetric
        # maze.
        for y, line in enumerate(matrix):
            for x, char in enumerate(line):
                if not g(x, y) and g(x - 1, y):
                    matrix[y][x - 1] = " "

        # Right now the maze has the correct aspect ratio, but is still using
        # 'O' to represent walls.

        # Finally we replace the walls with Unicode characters depending on
        # their context.
        for y, line in enumerate(matrix):
            for x, char in enumerate(line):
                if not g(x, y):
                    continue

                connections = {N, S, E, W}
                if not g(x, y + 1):
                    connections.remove(S)
                if not g(x, y - 1):
                    connections.remove(N)
                if not g(x + 1, y):
                    connections.remove(E)
                if not g(x - 1, y):
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

    def _get_random_position(self) -> Tuple[int, int]:
        """Returns a random position on the maze."""
        return (random.randrange(0, self.width),
                random.randrange(0, self.height))

    def get_matrix_with_start_end_position(self, random_pos: bool = False) -> np.ndarray:
        """Return a array with start and end position"""

        def check() -> bool:
            """Return whether the player and target location are valid"""
            if self.player is None and self.player == self.target and self.target is None:
                return False
            else:
                distance = calc_distance(self.player, self.target)
                if distance < self.min_distance:
                    return False
                return True

        if random_pos:
            while not check():
                self.player = self._get_random_position()
                self.target = self._get_random_position()
        else:
            while self.player is None or self.matrix[self.player[0]][self.player[1]] != " ":
                self.player = (random.randrange(0, self.height), 1)
            while self.target is None or self.matrix[self.target[0]][self.target[1]] != " ":
                self.target = (random.randrange(0, self.height), self.width * 2 - 1)

        matrix = self.matrix
        matrix[self.target] = TARGET
        matrix[self.player] = PLAYER

        return matrix

    @classmethod
    def generate(cls, width: int = 20, height: int = 10):
        """Returns a new random perfect maze with the given sizes."""
        m = cls(width, height)
        m.randomize()
        return m

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

        self.get_matrix_with_start_end_position()

        # data = {"start": [self.player], "end": [self.target]}

        return map_name


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
