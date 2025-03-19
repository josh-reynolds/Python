from enum import Enum
from engine import *

WIDTH = 960
HEIGHT = 540
TITLE = "Invader"

class KeyboardControls:         ###
    def update(self):
        pass                        ###
    def button_pressed(self, a):    ###
        pass                         ###

class State(Enum):
    TITLE = 1,
    ####

def update():
    global state, game, state_timer

    keyboard_controls.update()

    state_timer += 1

    if state == State.TITLE:
        for controls in (keyboard_controls,):     # comments indicate GitHub has controller support too
            if controls is not None and controls.button_pressed(0):
                state = State.PLAY
                state_timer = 0
                game = Game(Player(controls))
                break

    elif state == State.PLAY:
        if game.player.lives <= 0:
            state = State.GAME_OVER
            state_timer = 0
        else:
            game.update()

    elif state == State.GAME_OVER:
        game.update()
        if state_timer > 60:
            for controls in (keyboard_controls,):     # comments indicate GitHub has controller support too
                if controls is not None and controls.button_pressed(0):
                    state = State.TITLE
                    state_timer = 0
                    game = None
                    play_music("menu_theme")

def draw():
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit(f"start{(state_timer // 4) % 14}", (WIDTH // 2 - 350 // 2, 450))

    elif state == State.PLAY:
        game.draw()

    elif state == State.GAME_OVER:
        game.dxraw()
        draw_text("GAME OVER", WIDTH // 2, (HEIGHT // 2) - 100, True)

keyboard_controls = KeyboardControls()

state = State.TITLE
state_timer = 0

run()
