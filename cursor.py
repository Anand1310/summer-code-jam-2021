from blessed import Terminal
from blessed.colorspace import X11_COLORNAMES_TO_RGB, RGBColor

from utils import Vec  # type: ignore

DEFAULT_COLOUR = X11_COLORNAMES_TO_RGB["aqua"]
term = Terminal()


class Cursor:
    """Creates a Cursor Object that can be moved on command"""

    directions = {
        "KEY_UP": Vec(0, -1),
        "KEY_DOWN": Vec(0, 1),
        "KEY_LEFT": Vec(-1, 0),
        "KEY_RIGHT": Vec(1, 0),
    }

    def __init__(
        self,
        coords: Vec,
        fill: str = "██",
        colour: RGBColor = DEFAULT_COLOUR,
        speed: Vec = Vec(2, 1),
    ) -> None:

        self.coords = coords
        self.fill = fill
        self.colour = colour
        self.speed = speed
        self.term = term
        self.commands = {"r": self.show, "c": self.clear}

    def move(self, direction: str) -> str:
        """Moves the cursor to a new position based on direction and speed"""
        render_string = ""
        render_string += self.clear()
        directions = self.directions[direction]
        self.coords.x = min(
            max(self.coords.x + directions.x * self.speed.x, 0), self.term.width - 2
        )
        self.coords.y = min(
            max(self.coords.y + directions.y * self.speed.y, 0), self.term.height - 2
        )
        render_string += self.show()
        return render_string

    def clear(self) -> str:
        """Clears the rendered cursor"""
        return f"{self.term.move_xy(*self.coords)}" + " " * len(self.fill)

    def show(self) -> str:
        """Renders the cursor"""
        render_string = ""
        render_string += f"{self.term.move_xy(*self.coords)}"
        render_string += f"{self.term.color_rgb(*self.colour)}"
        render_string += f"{self.fill}{self.term.normal}"
        return render_string


def main() -> None:
    """A function to test the code"""
    Coords = Vec(5, 10)
    avi = Cursor(Coords)
    print(term.home + term.clear + term.normal, end="")
    print(
        f"{term.move_xy(*avi.coords)}{term.color_rgb(*avi.colour)}{avi.fill}{term.normal}"
    )
    with term.cbreak():
        val = ""
        i = 0
        while val.lower() != "q":
            val = term.inkey(timeout=0.05)
            if val.is_sequence:
                if 257 < val.code < 262:
                    print(term.home + term.move_down(i) + f"{val.code}")
                    i += 1
                    print(avi.move(val.name))
            else:
                if val.lower() == "r":
                    print(term.clear)
                    i = 0
                    print(avi.show())
                elif val.lower() == "c":
                    print(avi.clear())
        print(f"bye!{term.normal}{term.clear}")
    print(max(Coords))  # its a mutable object(!!)


if __name__ == "__main__":
    main()
