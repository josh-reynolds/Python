from enum import Enum
from engine import *

WIDTH = 480       ###
HEIGHT = 480      ###
TITLE = "Huevos"

MAX_REPLAYS = 1   ###

class KeyboardControls:
    NUM_BUTTONS = 2

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
        else:
            return keyboard.z

    def button_pressed(self, button):
        return self.is_pressed[button]

class Player:
    def __init__(self, a):   ###
        self.replay_data = 0    ###
        pass          ###

class Game:
    def __init__(self, a, b):   ###
        self.time_remaining = 0
        self.player = Player(1)   ###
        self.timer = 1   ###
    def draw(self):
        pass     ###
    def play_sound(self, a):   ###
        pass    ###

class TextAlign(Enum):
    RIGHT = 0   ###

def draw_text(a, b, c, align, font):   ###
    pass   ###

class State(Enum):
    TITLE = 1
    CONTROLS = 2
    PLAY = 3
    GAME_OVER = 4

def save_replays(a):   ###
    pass    ###

def update():
    global state, game, high_score, game_over_timer, all_replays, total_frames

    total_frames += 1
    keyboard_controls.update()

    def button_pressed_controls(button_num):
        for controls in (keyboard_controls,):
            if controls is not None and controls.button_pressed(button_num):
                return controls
        return None

    if state == State.TITLE:
        if button_pressed_controls(0) is not None:
            state = State.CONTROLS

    elif state == State.CONTROLS:
        controls = button_pressed_controls(0)
        if controls is not None:
            state = State.PLAY
            game = Game(Player(controls), all_replays)
            play_music("ingame_theme", 0.2)

    elif state == State.PLAY:
        if game.time_remaining <= 0:
            game.play_sound("gameover")
            state= State.GAME_OVER
            game_over_timer = 0

            all_replays.append(game.player.replay_data)

            if len(all_replays) > MAX_REPLAYS:
                all_replays.sort(key=lambda replay: len(replay), reverse=True)
                all_replays = all_replays[:MAX_REPLAYS]

            save_replays(all_replays)
        else:
            game.update()

    elif state == State.GAME_OVER:
        game_over_timer += 1
        if game_over_timer > 60 and keyboard_controls.button_pressed(0) is not None:
            if game.timer > high_score:
                high_score = game.timer
            state = State.TITLE
            play_music("title_theme")

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

def play_music(a, b=None):   ###
    pass   ###

keyboard_controls = KeyboardControls()
all_replays = []     ###
high_score = 0    ###

state = State.TITLE
total_frames = 0

run()
