import platform
from enum import Enum
import pygame
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Racer"

SPECIAL_FONT_SYMBOLS = {'xb_a':'%'}

fade_to_black_image = pygame.Surface((WIDTH,HEIGHT))

class Game:
    def draw(self):
        pass ###

def draw_text(a, b, c, d): ###
    pass ###

class State(Enum):
    TITLE = 1

def update():
    pass ###

def draw():
    game.draw()

    if state == State.TITLE:
        if demo_reset_timer < 1 or demo_start_timer < 1:
            value = demo_reset_timer if demo_reset_timer < 1 else demo_start_timer
            alpha = min(255, 255-(value*255))
            fade_to_black_image.set_alpha(alpha)
            fade_to_black_image.fill((0,0,0))
            screen.blit(fade_to_black_image, (0,0))

        text = f"PRESS {SPECIAL_FONT_SYMBOLS['xb_a']} OR" \
               f"{'Z' if 'Darwin' in platform.version() else 'LEFT CONTROL'}"
        draw_text(text, WIDTH // 2, HEIGHT - 82, True)

        logo_img = images.logo
        screen.blit(logo_img, (WIDTH//2 - logo_img.get_width() // 2,
                               HEIGHT//3 - logo_img.get_height() // 2))

state = State.TITLE
game = Game()
demo_reset_timer, demo_start_timer = 2 * 60, 0

run()
