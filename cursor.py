from blessed import Terminal
from blessed.colorspace import X11_COLORNAMES_TO_RGB, RGBColor

from utilities import Vec

DEFAULT_COLOUR = X11_COLORNAMES_TO_RGB["aqua"]


class Cursor:
    """Creates a Cursor Object that can be moved on command"""

    def __init__(
        self,
        coords: Vec,
        term: Terminal,
        fill: str = "██",
        colour: RGBColor = DEFAULT_COLOUR,
        speed: int = 2,
    ) -> None:

        self.coords = coords
        self.fill = fill
        self.colour = colour
        self.speed = speed
        self.term = term
        self.commands = {"r": self.render, "c": self.clear}

    directions = {
        "KEY_UP": Vec(0, -1),
        "KEY_DOWN": Vec(0, 1),
        "KEY_LEFT": Vec(-1, 0),
        "KEY_RIGHT": Vec(1, 0),
    }

    def move(self, direction: str) -> str:
        """Moves the cursor to a new position based on direction and speed"""
        render_string = []
        render_string.append(self.clear())
        directions = Cursor.directions[direction]
        self.coords.x = min(
            max(self.coords.x + directions.x * self.speed, 0), self.term.width - 2
        )
        self.coords.y = min(
            max(self.coords.y + directions.y * self.speed, 0), self.term.height - 2
        )
        # self.coords += Avatar.directions[direction]
        render_string.append(self.render())
        return "".join(render_string)

    def clear(self) -> str:
        """Clears the rendered cursor"""
        return f"{self.term.move_xy(*self.coords)}  "

    def render(self) -> str:
        """Renders the cursor"""
        render_string = []
        render_string.append(f"{self.term.move_xy(*self.coords)}")
        render_string.append(f"{self.term.color_rgb(*self.colour)}")
        render_string.append(f"{self.fill}{self.term.normal}")
        return "".join(render_string)


def main() -> None:
    """A function to test the code"""
    from blessed import Terminal

    term = Terminal()
    Coords = Vec(5, 10)
    avi = Cursor(Coords, term)
    print(term.home + term.clear + term.normal, end="")
    print(term.height, term.width)
    print(
        f"{term.move_xy(*avi.coords)}{term.color_rgb(*avi.colour)}{avi.fill}{term.normal}"
    )
    with term.cbreak():
        val = ""
        while val.lower() != "q":
            val = term.inkey(timeout=3)
            if val.is_sequence:
                if 257 < val.code < 262:
                    print(term.home + term.clear_eol + str(avi.coords))
                    print(avi.move(val.name))
            else:
                if val.lower() == "r":
                    print(avi.render())
                elif val.lower() == "c":
                    print(avi.clear())
        print(f"bye!{term.normal}")
    print(max(Coords))


if __name__ == "__main__":
    main()
