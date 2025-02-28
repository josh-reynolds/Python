from enum import Enum

WIDTH = 400    ###
HEIGHT = 400    ###
TITLE = "Futbol"

class Game():
    def draw(self):
        pass

class State(Enum):
    MENU = 0,
    PLAY = 1,
    GAME_OVER = 2

class MenuState(Enum):
    NUM_PLAYERS = 0,
    DIFFICULTY = 1

def update():
    pass

def draw():
    game.draw()

    if state == State.MENU:
        if menu_state == MenuState.NUM_PLAYERS:
            image = "menu0" + str(menu_num_players)
        else:
            image = "menu1" + str(menu_difficulty)
        screen.blit(image, (0,0))

    elif state == State.PLAY:
        screen.blit("bar", (HALF_WINDOW_W - 176, 0))

        for i in range(2):
            screen.blit("s" + str(game.teams[i].score), (HALF_WINDOW_W + 7 - 39 * i, 6))

        if game.score_timer > 0:
            screen.blit("goal", (HALF_WINDOW_W - 300, HEIGHT / 2 - 88 ))

    elif state == State.GAME_OVER:
        img = "over" + str(int(game.teams[1].score > game.teams[0].score))
        screen.blit(img, (0,0))

        for i in range(2):
            img = "l" + str(i) + str(game.teams[i].score)
            screen.blit(img, (HALF_WINDOW_W + 25 - 125 * i, 144))

state = State.MENU
menu_state = MenuState.NUM_PLAYERS
menu_num_players = 1

game = Game()

#----------------------
from engine import run
run()

