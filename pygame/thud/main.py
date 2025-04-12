from enum import Enum
from engine import *

WIDTH = 400     ###
HEIGHT = 400    ###
TITLE = "Thud!"

SPECIAL_FONT_SYMBOLS = {'xb_a':1}

class KeyboardControls:
    def update(self):
        pass   ###
    def button_pressed(self, a):   ###
        pass   ###

def get_char_image_and_width(a): ###
    return None,10 ###

def text_width(a):  ###
    return 10  ###

def draw_text(text, x, y, center=False):
    if center:
        x -= text_width(text) // 2

    start_x = x

    for char in text:
        if char == "\n":
            y += 35
            x = start_x
        else:
            image, width = get_char_image_and_width(char)
            if image is not None:
                screen.blit(image, (x,y))
            x += width

class State(Enum):
    TITLE = 1

def update():
    global state, game, total_frames

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
            game = Game(controls)

    elif state == State.PLAY:
        game.update()
        if game.player_lives <= 0 or game.check_won():
            gaem.shutdown()
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        if button_pressed_controls(0) is not None:
            state = State.TITLE
            game = None

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

keyboard_controls = KeyboardControls()

state = State.TITLE

run()
