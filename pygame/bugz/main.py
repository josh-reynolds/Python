from enum import Enum

WIDTH = 480
HEIGHT = 800
TITLE = "Bugz!"

class Game():
    def __init__(self):
        self.time = 0

    def draw(self):
        pass

def update():
    pass

class State(Enum):
    MENU = 1,
    PLAY = 2,
    GAME_OVER = 3

def draw():
    game.draw()

    if state == State.MENU:
        screen.blit("title", (0,0))
        screen.blit("space" + str((game.time // 4) % 14), (0, 240))

    elif state == State.PLAY:
        for i in range(game.player.lives):
            screen.blit("life", (i*40+8, 4))

        score = str(game.score)

        for i in range(1, len(score)+1):
            digit = score[-i]
            screen.blit("digit"+digit, (468-i*24, 5))

    elif state == State.GAME_OVER:
        screen.blit("over", (0,0))

state = State.MENU
game = Game()

#----------------------
from engine import run
run()
