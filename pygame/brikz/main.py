from enum import Enum
import pygame
from engine import *

WIDTH = 800                  ###
HEIGHT = 480                 ###
TITLE = 'Brikz'

class AIControls:         ###
    def update(self):     ###
        pass              ###

class KeyboardControls:      ###
    def update(self):     ###
        pass              ###
    def fire_pressed(self):
        pass                  ###

class Game:               ###
    def __init__(self, a):   ###
        pass               ###
    def update(self):     ###
        pass              ###
    def draw(self):       ###
        pass              ###

def get_joystick_if_exists():
    return pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None

def setup_joystick_controls():
    global joystick_controls
    joystick = get_joystick_if_exists()
    joystick_controls = JoystickControls(joystick) if joystick is not None else None

def update_controls():
    keyboard_controls.update()
    if joystick_controls is None:
        setup_joystick_controls()
    if joystick_controls is not None:
        joystick_controls.update()

class State(Enum):
    TITLE = 1,
    PLAY = 2,
    GAME_OVER = 3

def update():
    global state, game, total_frames
    total_frames += 1

    update_controls()

    if state == State.TITLE:
        ai_controls.update()
        game.update()

        for controls in (keyboard_controls, joystick_controls):
            if controls is not None and controls.fire_pressed():
                game = Game(controls)
                state = State.PLAY
                stop_music()
                break

    elif state == State.PLAY:
        if game.lives > 0:
            game.update()
        else:
            game.play_sound("game_over")
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        for controls in (keyboard_controls, joystick_controls):
            if controls is not None and controls.fire_pressed():
                game = Game(ai_controls)
                state = State.TITLE
                play_music("title_theme")

def draw():
    game.draw()
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit("startgame", (20,80))
        screen.blit(f"start{(total_frames // 4) % 13}", (WIDTH//2 - 250//2, 530))
    elif state == State.GAME_OVER:
        screen.blit(f"gameover{(total_frames // 4) % 15}", (WIDTH//2 - 450//2, 450))

keyboard_controls = KeyboardControls()
ai_controls = AIControls()
setup_joystick_controls()

state = State.TITLE
game = Game(ai_controls)
total_frames = 0

run()
