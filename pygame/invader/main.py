from enum import Enum
from engine import *

WIDTH = 960
HEIGHT = 540
TITLE = "Invader"


class State(Enum):
    TITLE = 1,
    ####

def update():
    pass

def draw():
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit(f"start{(state_timer // 4) % 14}", (WIDTH // 2 - 350 // 2, 450))

    elif state == State.PLAY:
        game.draw()

    elif state == State.GAME_OVER:
        game.dxraw()
        draw_text("GAME OVER", WIDTH // 2, (HEIGHT // 2) - 100, True)

state = State.TITLE
state_timer = 0

run()
