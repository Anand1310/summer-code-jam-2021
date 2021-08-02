import copy
import logging
import os
import time

from openal import oalOpen

from maze_gitb.utils import Vec  # type: ignore

dirname = os.path.dirname(__file__)

enter_box_sound = oalOpen(os.path.join(dirname, "..", "sound/enter_box.wav"))
hit_wall_sound = oalOpen(os.path.join(dirname, "..", "sound/hit_wall.wav"))
level_up_sound = oalOpen(os.path.join(dirname, "..", "sound/level_up.wav"))
bgm = oalOpen(os.path.join(dirname, "..", "sound/bgm.wav"))
start_screen_music = oalOpen(os.path.join(dirname, "..", "sound/start.wav"))
wind_sound = oalOpen(os.path.join(dirname, "..", "sound/wind.wav"))

echo = oalOpen(os.path.join(dirname, "..", "sound/first_echo.wav"))
echo_2 = oalOpen(os.path.join(dirname, "..", "sound/second_echo.wav"))


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
    """Play first echo sound effect"""
    k = copy.copy(direction)
    if direction.x != 0:
        k.x += int(distance) * 0.7
    else:
        k.y += int(distance) * 0.7
    logging.info(f"{k.x}, {k.y}")
    echo.play()
    time.sleep(abs(distance) / 5)
    play_echo_2(direction, distance)


def play_echo_2(direction: Vec, distance: int) -> None:
    """Play second echo sound effect"""
    k = copy.copy(direction)
    if direction.x != 0:
        k.x += int(distance)
    else:
        k.y += int(distance)
    logging.info(f"{k.x}, {k.y}")
    echo_2.set_position((k.x, 0, k.y))
    echo_2.play()
