# Getting Inside The Box

This game was developed by the team [**Benevolent Bonobos**](#About-Us), during the [Summer Code Jam 2021](https://pythondiscord.com/events/code-jams/8/) held by [Python Discord](https://discord.com/invite/python).

Teams that participated in the code jam had to create a TUI based on the theme _Think Inside the Box_.

[![Youtube Link](http://img.youtube.com/vi/ERME3fjnfFE/0.jpg)](http://www.youtube.com/watch?v=ERME3fjnfFE "Video Title")


## Contents
- [How To Play](#how-to-play)
- [Requirements](#requirements)
- [Installation](#installation)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [About Us](#about-us)


<!--- This can go now that How To Play covers everything
### Normal mode

- with 9 levels

### Infinite mode

- with infinite levels
- no ending
- press `q` to quit --->

## How To Play
<!-- Insert the tutorial we made in the game here?-->
<!-- The video goes here? -->
1. There are 6 options in start menu:
    - Start: Play the normal levels.
    - Infinite: Never ending gameplay.
    - Tutorial: How to play.
    - Credits
    - Leaderboard
    - Quit
2. Use **arrow keys** to move.
3. On starting, a glimpse of the whole maze will be shown. After it disappears, the game will start.
4. Player has to reach `&` with minimum collisions with the walls and in minimum time.
5. Boxes:
    - The place to stop and think.
    - Will show the part of the maze associated with the box.
    - Time slows down here.
6. Echolocation:
    - Press `e` to make a noise.
    - An echo will come from the direction in which player last moved.
    - The echo will get stronger the nearer the player is to the wall.
7. Persistence:
    - It acts as a score for a player.
    - Higher is better.
    - It will decrease with time.
    - It will decrease more and more with each collision.
    - Since time slows down in a box, persistence will decrease slower inside the box.
    - It is visible in the top right corner.
8. In the top left corner, the number of collisions made in the current level is visible.
9. On pressing `q`, the game will be paused. There will be an option to _play again_ or _quit_.
10. In normal mode, a player can play 9 levels.
11. In infinite mode, a player will have to press `q` for quitting.
12. After completing all normal levels, a player, if they want, can put their name in the _leaderboard_ which stores their score.

## Requirements

- Python 3.8.6 or greater
- A stereo headset (for echolocation)
- The terminal window should be sufficiently large (At least `50 x 15` characters in width and height). You should not resize the terminal during the game.

## Installation

### 1. Clone the repository

```sh
git clone https://github.com/Anand1310/summer-code-jam-2021.git
cd summer-code-jam-2021
```

### 2. Install required dependencies

#### Windows
<!-- Not sure about Mac-->
```sh
pip install -r dev-requirements.txt
```

#### Linux

```sh
apt-get install openal-soft
pip3 install -r dev-requirements.txt
```

### 3. Run the game

#### Windows

```sh
python main.py
```

#### Linux

```sh
python3 main.py
```
| Note: |
| :--- |
|The player should visit the _tutorial_ for a hands-on understanding of the game.|

## Screenshots

![First view](images/first_view.png)

![Box view](images/box_view.png)

![Box view](images/box_view3.png)

![Without box view](images/without_box.png)

![Box view](images/box_view2.png)

![Box view](images/gameplay.gif)

## Future Improvements


- Reveal the map with animation at the start of the level.
- Allow player to move during echo.
- Fix bug: Hitting leaderboard in the main menu exits game. (This can be fixed with [this change](https://github.com/pritam-dey3/summer-code-jam-2021/commit/64eb2852514e91749fe706433363a8941d290d6c), we shall update the repo once the code jam finishes.)
- Fix bug: Game background music does not start on tutorial. (This can also be fixed by [this commit.](https://github.com/pritam-dey3/summer-code-jam-2021/commit/a010bab5a2360cf26d99b25f5f185ef5a578b67d))
- Add _Main menu_ option in pause menu. ([This](https://github.com/pritam-dey3/summer-code-jam-2021/commit/3368968c668307b36278629b75b02433fca18592) will do it)

## About Us


<!--Add your own github link here-->
- [Anand](https://github.com/Anand1310)
- [Pritam Dey](https://github.com/pritam-dey3)
- [Himi](https://github.com/hizv)
- [Olivia](https://github.com/OliviaVespera)
- [StoneSteel](https://github.com/StoneSteel27)
- [Jason Ho](https://github.com/Jason11ookJJ)
