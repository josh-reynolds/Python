from enum import Enum
from engine import *

WIDTH = 480       ###
HEIGHT = 480      ###
TITLE = "Huevos"

class State(Enum):
    TITLE = 1

def update():
    pass         ###

def draw():
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit("press_to_start", (0,0))
        anim_frame = (total_frames // 6) % 11
        screen.blit("start" + str(anim_frame), (WIDTH//2 - 150, 360))

    elif state == State.CONTROLS:
        screen.fill((0,0,0))
        screen.blit("controls", (0,0))

    elif state == State.PLAY:
        game.draw()

    elif state == State.GAME_OVER:
        screen.fill((0, 54, 255))

        anim_frame = (total_frames // 5) % 14
        screen.blit(f"gameover{anim_frame}", (WIDTH//2 - 625//2, 100))

        seconds = int(game.timer / 60)
        if seconds >= 60:
            screen.blit("survived_for_mins_seconds", (0,0))
            draw_text(f"{seconds//60}", 180, 270, align=TextAlign.RIGHT, font="fontlrg")
            draw_text(f"{seconds%60}", 470, 270, align-TextAlign.CENTER, font="fontlrg")
        else:
            screen.blit("survived_for_seconds", (0,0))
            draw_text(f"{seconds}", 300, 310, align=TextAlign.RIGHT, font="fontlrg")

        if game.timer > high_score:
            anim_frame = (total_frames // 5) % 8
            screen.blit(f"newrecord{anim_frame}", (WIDTH // 2 - 575 // 2, 380))

state = State.TITLE
total_frames = 0

run()
