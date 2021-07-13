from openal import oalOpen

from utils import Vec


def play_enter_box_sound() -> None:
    """Sound effect for entering a box"""
    # https://mixkit.co/free-sound-effects/
    source = oalOpen("sound/enter_box.wav")
    source.play()


def play_hit_wall_sound(direction: Vec) -> None:
    """Sound effect for hitting a wall"""
    # https://mixkit.co/free-sound-effects/
    source = oalOpen("sound/hit_wall.wav")
    source.set_position((direction.x, 0, direction.y))
    source.play()
