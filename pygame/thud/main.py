from enum import Enum
from engine import *

WIDTH = 400     ###
HEIGHT = 400    ###
TITLE = "Thud!"

SPECIAL_FONT_SYMBOLS = {'xb_a':1}

def draw_text(a, b, c, d):   ###
    pass   ###

class State(Enum):
    TITLE = 1

def update():
    pass     ###

def draw():
    if state == State.TITLE:
        logo_img = images.title0 if total_frames // 20 % 2 == 0 else images.title1
        screen.blit(logo_img, (WIDTH//2 - logo_img.get_width() // 2,
                               HEIGHT//2 - logo_img.get_height() // 2))
        draw_text(f"PRESS {SPECIAL_FONT_SYMBOLS['xb_a']} OR Z",
                  WIDTH//2, HEIGHT - 50, True)

    elif state == State.CONTROLS:
        screen.fill((0,0,0))
        sreen.blit("menu_controls", (0,0))

    elif state == State.PLAY:
        game.draw()

    elif state == State.GAME_OVER:
        img = images.status_win if game.check_won() else images.status_lose
        screen.blit(img, (WIDTH//2 - img.get_width() // 2,
                          HEIGHT//2 - img.get_height() // 2))

total_frames = 0
state = State.TITLE

run()
