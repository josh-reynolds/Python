from enum import Enum


WIDTH = 800
HEIGHT = 480
TITLE = "Run Rabbit Run"

class keys:
    SPACE = None

def key_just_pressed(x):
    pass

class Game():
    def __init__(self):
        self.scroll_pos = 1

    def update(self):
        pass

    def draw(self):
        pass

class State(Enum):
    MENU = 1,
    PLAY = 2,
    GAME_OVER = 3

def update():
    global state, game, high_score

    if state == State.MENU:
        if key_just_pressed(keys.SPACE):
            state = State.PLAY
            game = Game(Rabbit((240, -320)))
        else:
            game.update()

    elif state == State.PLAY:
        if game.rabbit.state != PlayerState.ALIVE and game.rabbit.timer < 0:
            high_score = max(high_score, game.score())

            try:
                with open("high.txt", "w") as file:
                    file.write(str(high_score))
            except:
                pass

            state = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if key_just_pressed(keys.SPACE):
            game.stop_looped_sounds()
            state = State.MENU
            game = Game()

def draw():
    game.draw()

    if state == State.MENU:
        screen.blit('title', (0,0))
        screen.blit('start' + str([0,1,2,1][game.scroll_pos // 6 % 4]),
                    ((WIDTH - 270) // 2, HEIGHT - 240))

    elif state == State.PLAY:
        display_number(game.score(), 0, 0, 0)
        display_number(high_score, 1, WIDTH - 10, 1)

    elif state == State.GAME_OVER:
        screen.blit("gameover", (0,0))

state = State.MENU
game = Game()

#-----------------------
from engine import run
run()
