"""Convert copied maze from asciiflow to matrix

┌───────────────────┐
│xxxxxxxxxx xxxxx xx│
│xxx        x   x xx│
│xxx xxx   xx   x   │
│    x xxxxx    xxxxx
xxxxxx   x          │
│    xxxxx   xxxx   │
│xxx     xxxxx  x xx│
│xxxxxxx        xxx │
└───────────────────┘
"""

from pprint import pprint
from typing import List

from pyperclip import paste

ascii = paste()
map: List[List[int]] = []

for i, line in enumerate(ascii.split("\n")):
    map.append([])
    for char in line.strip():
        map[i].append(int(char != "x"))

pprint(map[1:])
