from enum import Enum
import pygame
from engine import *

WIDTH = 800                  ###
HEIGHT = 480                 ###
TITLE = 'Brikz'


LEVELS = [0,0,0]       ###

class Mock:      ###
    def __init__(self):           ###
        self.shadow = MockShadow()        ###
    def draw(self):        ###
        pass                 ###

class MockShadow:           ###
    def draw(self):        ###
        pass                 ###

class AIControls:         ###
    def update(self):     ###
        pass              ###

class KeyboardControls:      ###
    def update(self):     ###
        pass              ###
    def fire_pressed(self):
        pass                  ###

class Game:
    def __init__(self, controls=None, lives=3):
        self.controls = controls if controls else AIControls()
        self.lives = lives
        self.score = 0
        self.new_level(0)

    def new_level(self, a):     ####
        self.level_num = 0       ###
        self.portal_frame = 0       ###
        self.shadow_surface = "placeholder"    ###
        self.brick_surface = "placeholder"    ###
        self.barrels =[Mock()]          ###
        self.balls =[Mock()]          ###
        self.bullets =[Mock()]          ###
        self.impacts =[Mock()]          ###
        self.bat = Mock()                  ###

    def update(self):     ###
        pass              ###

    def draw(self):
        screen.blit(f"arena{self.level_num % len(LEVELS)}", (0,0))
        screen.blit(f"portal_exit{self.portal_frame}", (WIDTH - 70 - 20, HEIGHT - 70))
        screen.blit(f"portal_meanie00", (110,40))
        screen.blit(f"portal_meanie10", (440,40))

        screen.surface.set_clip((20, 42, 600, 598))

        screen.blit(self.shadow_surface, (0, 0))

        for obj in self.barrels + self.balls + [self.bat]:
            obj.shadow.draw()

        screen.blit(self.brick_surface, (0, 0))

        for obj in self.balls + [self.bat] + self.barrels + self.bullets:
            obj.draw()

        screen.surface.set_clip(None)

        for obj in self.impacts:
            obj.draw()

        if not self.in_demo_mode():
            self.draw_score()
            self.draw_lives()

    def draw_score(self):
        x = 0
        for digit in str(self.score):
            image = "digit" + digit
            screen.blit(image, (x, 50))
            x += 55

    def draw_lives(self):
        x = 0
        for i in range(self.lives):
            screen.blit("life", (x, HEIGHT-20))
            x += 50

    def in_demo_mode(self):
        return isinstance(self.controls, AIControls)

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
