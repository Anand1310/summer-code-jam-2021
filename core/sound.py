from openal import oalOpen

from utils import Vec  # type: ignore

enter_box_sound = oalOpen("sound/enter_box.wav")
hit_wall_sound = oalOpen("sound/hit_wall.wav")
level_up_sound = oalOpen("sound/level_up.wav")
bgm = oalOpen("sound/bgm.wav")
start_screen_music = oalOpen("sound/start.wav")
wind_sound = oalOpen("sound/wind.wav")


def play_enter_box_sound() -> None:
    """Sound effect for entering a box"""
    # https://mixkit.co/free-sound-effects/
    enter_box_sound.play()


def play_hit_wall_sound(direction: Vec) -> None:
    """Sound effect for hitting a wall"""
    # https://mixkit.co/free-sound-effects/
    hit_wall_sound.set_position((direction.x, 0, direction.y))
    hit_wall_sound.play()


def play_level_up_sound() -> None:
    """Sound effect for hitting a wall"""
    # https://mixkit.co/free-sound-effects/
    level_up_sound.play()


def play_bgm() -> None:
    """Play bgm"""
    bgm.set_looping(True)
    bgm.set_gain(0.2)
    bgm.play()


def stop_bgm() -> None:
    """Stop bgm"""
    bgm.stop()


def play_start_bgm() -> None:
    """Play start scene music"""
    start_screen_music.set_looping(True)
    start_screen_music.play()


def stop_start_bgm() -> None:
    """End start scene music"""
    start_screen_music.stop()


def enter_game_sound() -> None:
    """Stop starting scene bgm start the main bgm"""
    stop_start_bgm()
    play_bgm()


def play_echo(direction: Vec, distance: int) -> None:
    """Play echo sound effect"""
    if direction.x != 0:
        direction.x += int(distance)
    else:
        direction.y += int(distance)
    wind_sound.set_position((direction.x, 0, direction.y))
    wind_sound.play()
