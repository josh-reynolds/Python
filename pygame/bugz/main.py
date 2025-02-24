from enum import Enum
from engine import keyboard

WIDTH = 480
HEIGHT = 800
TITLE = "Bugz!"

num_grid_rows = 10
num_grid_cols = 10

class Game():
    def __init__(self, player=None):
        self.wave = -1
        self.time = 0
        self.player = player
        self.grid = [[None] * num_grid_cols for y in range(num_grid_rows)]
        self.bullets = []
        self.explosions = []
        self.segments = []
        self.flying_enemy = None
        self.score = 0

    def update(self):
        pass

    def draw(self):
        pass

def space_pressed():
    global space_down
    if keyboard.space:
        if not space_down:
            space_down = True
            return True
    else:
        space_down = False
        return False

class State(Enum):
    MENU = 1,
    PLAY = 2,
    GAME_OVER = 3

def update():
    global state, game

    if state == State.MENU:
        if space_pressed():
            state = State.PLAY
            game = Game(Player((240, 768)))

        game.update()

    elif state == State.PLAY:
        if game.player.lives == 0 and game.player.timer == 100:
            sounds.gameover.play()
            sstate = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if space_pressed():
            state = State.MENU
            game = Game()

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
