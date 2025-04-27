import platform
from enum import Enum
import pygame
from pygame.math import Vector2, Vector3
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Racer"

FIXED_TIMESTEP = 1 ###

SPECIAL_FONT_SYMBOLS = {'xb_a':'%'}

fade_to_black_image = pygame.Surface((WIDTH,HEIGHT))

def draw_text(a, b, c, d): ###
    pass ###

class KeyboardControls:
    def update(self):
        pass ###
    def button_pressed(self, a):  ###
        pass ###
def make_track():
    pass ###

class Game:
    def __init__(self, controls=None):
        self.track = make_track()
        self.player_car = None
        self.camera_follow_car = None
        self.setup_cars(controls)
        self.camera = Vector3(0, 400, 0)
        self.background = images.background
        self.bg_offset = Vector2(-self.background.get_width() // 2, 30)
        self.first_frame = True
        self.frame_counter = 0
        self.timer = 0
        self.race_complete = False
        self.time_up = False
        if self.player_car is not None:
            self.start_timer = 3.999
            play_music("engines_startline")
        else:
            self.start_timer = 0

    def setup_cars(self, a): ###
        pass ###
    def update(self, a): ###
        pass ###
    def draw(self):
        pass ###

def update_controls():
    keyboard_controls.update()

class State(Enum):
    TITLE = 1

def update(delta_time):
    global state, game, accumulated_time, demo_reset_timer, demo_start_timer

    update_controls()

    def button_pressed_controls(button_num):
        for controls in (keyboard_controls,):
            if controls is not None and controls.button_pressed(button_num):
                return controls
        return None

    if state == State.TITLE:
        controls = button_pressed_controls(0)
        if controls is not None:
            state = State.PLAY
            game = Game(controls)

        demo_reset_timer -= delta_time
        demo_start_timer += delta_time
        if demo_reset_timer <= 0:
            game = Game()
            demo_reset_timer = 60 * 2
            demo_start_timer = 0

    elif state == State.PLAY:
        if game.race_complete:
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        if button_pressed_controls(0) is not None:
            game.player_car.stop_engine_sound()
            state = State.TITLE
            game = Game()
            play_music("title_theme")

    accumulated_time += delta_time
    while accumulated_time >= FIXED_TIMESTEP:
        accumulated_time -= FIXED_TIMESTEP
        game.update(FIXED_TIMESTEP)

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

keyboard_controls = KeyboardControls()
state = State.TITLE
game = Game()
demo_reset_timer, demo_start_timer = 2 * 60, 0
accumulated_time = 0

run()
