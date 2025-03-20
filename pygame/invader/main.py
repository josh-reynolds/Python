import math
from enum import Enum
import pygame
from pygame.math import Vector2
from engine import *

WIDTH = 960
HEIGHT = 540
TITLE = "Invader"

LEVEL_WIDTH = 500               ###
TERRAIN_OFFSET_Y = 5               ###

class KeyboardControls:
    NUM_BUTTONS = 1

    def __init__(self):
        self.previously_down = [False for i in range(KeyboardControls.NUM_BUTTONS)]
        self.is_pressed = [False for i in range(KeyboardControls.NUM_BUTTONS)]

    def update(self):
        for button in range(KeyboardControls.NUM_BUTTONS):
            button_down = self.button_down(button)
            self.is_pressed[button] = button_down and not self.previously_down[button]
            self.previously_down[button] = button_down

    def button_down(self, button):
        if button == 0:
            return keyboard.space

    def button_pressed(self, button):
        return self.is_pressed[button]

class Player:
    def __init__(self, a):        ###
        self.lives = 3                 ###
        self.facing_x = 1          ###
        self.velocity = Vector2(0,0)    ###
        self.x = 1                   ###
        self.y = 1                   ###
        self.tilt_y = 1                   ###
    def draw(self, a, b):               ###
        pass                     ###

class Radar:
    pass              ###

class Game:
    def __init__(self, player):
        self.player = player
        self.radar = Radar()
        self.enemies, self.humans, self.lasers, self.bullets = [], [], [], []
        self.score = 0
        self.wave = 0
        self.wave_timer = 0
        self.timer = 0
        self.player_camera_offset_x = WIDTH / 3
        self.terrain_surface = images.terrain
        self.terrain_mask = pygame.mask.from_surface(self.terrain_surface)
        self.new_wave()
        play_music("ambience")

    def new_wave(self):
        pass               ###

    def update(self):
        pass                 ###

    def draw(self):
        if self.player.facing_x > 0:
            target_camera_offset_x = WIDTH / 3
        else:
            target_camera_offset_x = 2 * WIDTH / 3

        target_camera_offset_x -= self.player.velocity.x * 15
        camera_offset_delta = min(8, max(-8, (target_camera_offset_x - self.player_camera_offset_x)/20))

        self.player_camera_offset_x = math.floor(self.player_camera_offset_x + camera_offset_delta)

        left = -(int(self.player.x - self.player_camera_offset_x) % LEVEL_WIDTH)
        top = max(-int(self.player.y / 4), -100)

        bg_width = images.background.get_width()
        for i in range(5):
            screen.blit("background", (left // 2 + bg_width * i, top // 2))

        screen.blit(self.terrain_surface, (left, top + TERRAIN_OFFSET_Y))
        screen.blit(self.terrain_surface, (left + LEVEL_WIDTH, top + TERRAIN_OFFSET_Y))

        offset_x = -(self.player.x - self.player_camera_offset_x)

        for obj in self.bullets + self.humans + self.enemies + \
                (self.lasers + [self.player] if self.player.tilt_y == 1 
                 else [self.player] + self.lasers):
                    obj.draw(offset_x, top)

        self.draw_ui()

    def draw_ui(self):
        pass              ###

class State(Enum):
    TITLE = 1
    PLAY = 2
    GAME_OVER = 3

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

def play_music(name):
    try:
        music.play(name)
    #except Exception:
        #pass
    except Exception as e:         ###
        print(e)                   ###

keyboard_controls = KeyboardControls()

state = State.TITLE
state_timer = 0

run()
