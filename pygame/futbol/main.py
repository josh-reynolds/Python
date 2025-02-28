from enum import Enum
from engine import keys, keyboard

WIDTH = 400    ###
HEIGHT = 400    ###
TITLE = "Futbol"

HALF_WINDOW_W = 100

class Team():                 ###
    def __init__(self):       ###
        self.score = 0        ###

class Game():
    def __init__(self, a=None, b=None, c=None):
        self.teams = [Team(),Team()]        ###
        self.score_timer = 0                ###
    def update(self):
        pass
    def draw(self):
        pass

key_status = {}

def key_just_pressed(key):
    result = False

    prev_status = key_status.get(key, False)

    if not prev_status and keyboard[key]:
        result = True

    key_status[key] = keyboard[key]

    return result

class Controls:
    def __init__(self, player_num):
        if player_num == 0:
            self.key_up = keys.UP
            self.key_down = keys.DOWN
            self.key_left = keys.LEFT
            self.key_right = keys.RIGHT
            self.key_shoot = keys.SPACE
        else:
            self.key_up = keys.W
            self.key_down = keys.S
            self.key_left = keys.A
            self.key_right = keys.D
            self.key_shoot = keys.LSHIFT


class State(Enum):
    MENU = 0,
    PLAY = 1,
    GAME_OVER = 2

class MenuState(Enum):
    NUM_PLAYERS = 0,
    DIFFICULTY = 1

def update():
    global state, game, menu_state, menu_num_players, menu_difficulty

    if state == State.MENU:
        if key_just_pressed(keys.SPACE):
            if menu_state == MenuState.NUM_PLAYERS:
                if menu_num_players == 1:
                    menu_state = MenuState.DIFFICULTY
                else:
                    state = State.PLAY
                    menu_state = None
                    game = Game(Controls(0), Controls(1))
            else:
                state = State.PLAY
                menu_state = None
                game = Game(Controls(0), None, menu_difficulty)
        else:
            selection_change = 0
            if key_just_pressed(keys.DOWN):
                selection_change = 1
            elif key_just_pressed(keys.UP):
                selection_change = -1
            if selection_change != 0:
                sounds.move.play()
                if menu_state == MenuState.NUM_PLAYERS:
                    menu_num_players == 2 if menu_num_players == 1 else 1
                else:
                    menu_difficulty = (menu_difficulty + selection_change) % 3

        game.update()

    elif state == State.PLAY:
        if max([team.score for team in game.teams]) == 9 and game.score_timer == 1:
            state = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if key_just_pressed(keys.SPACE):
            state = State.MENU
            menu_state = MenuState.NUM_PLAYERS
            game = Game()

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
menu_difficulty = 0

game = Game()

#----------------------
from engine import run
run()

