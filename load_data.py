import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from game import Box
from utils import Vec


def load_map(file: Path) -> np.ndarray:
    """Load map from file and return numpy array"""
    with open(file, "r", encoding="utf-8") as f:
        txt = f.readlines()

    map: np.ndarray = np.ndarray((len(txt), len(txt[0])), dtype=np.dtype("<U1"))

    for i, line in enumerate(txt):
        for j, chr in enumerate(line):
            map[i, j] = chr
    return np.delete(map, -1, axis=1)


def load_level(level: int) -> Tuple[np.ndarray, Vec, Vec, List[Box]]:
    """Load level from the corresponding folder"""
    levels_path = Path("levels").joinpath(str(level))

    main_maze = load_map(levels_path.joinpath("map.txt"))
    with open(levels_path.joinpath("info.json"), "r") as f:
        data: Dict = json.load(f)
    start_loc = Vec(*data.pop("start"))
    end_locs = [Vec(*loc) for loc in data.pop("end")]

    boxes: List[Box] = []
    for box in data.values():
        loc = Vec(*box.pop("coords"))
        maze = load_map(levels_path.joinpath(box.pop("map_file")))
        boxes.append(Box(loc, maze))

    return main_maze, start_loc, end_locs, boxes
