from openal import oalOpen

from utils import Vec

enter_box_sound = oalOpen("sound/enter_box.wav")
hit_wall_sound = oalOpen("sound/hit_wall.wav")


def play_enter_box_sound() -> None:
    """Sound effect for entering a box"""
    # https://mixkit.co/free-sound-effects/
    enter_box_sound.play()


def play_hit_wall_sound(direction: Vec) -> None:
    """Sound effect for hitting a wall"""
    # https://mixkit.co/free-sound-effects/
    hit_wall_sound.set_position((direction.x, 0, direction.y))
    hit_wall_sound.play()
