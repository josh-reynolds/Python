import sys
from random import choice, randint, random, shuffle
from enum import Enum
import pygame
from engine import Actor, music, keyboard

if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

WIDTH = 800
HEIGHT = 480
TITLE = "Cave"

class Player():
    def __init__(self):
        self.lives = 3
        self.score = 0
        self.health = 1

class Game():
    def __init__(self, player=None):
        self.timer = 0
        self.player = player
        self.level = 0

    def update(self):
        pass
    
    def draw(self):
        pass

CHAR_WIDTH = [27]

def char_width(char):
    return 10

def draw_text(text, y, x=None):
    if x == None:
        x = (WIDTH - sum([char_width(c) for c in text])) // 2

    for char in text:
        screen.blit("font0" + str(ord(char)), (x, y))
        x += char_width(char)

IMAGE_WIDTH = {"life":44, "plus":40, "health":40}

def draw_status():
    number_width = CHAR_WIDTH[0]
    s = str(game.player.score)
    draw_text(s, 451, WIDTH - 2 - (number_width * len(s)))
    draw_text("LEVEL " + str(game.level + 1), 451)

    lives_health = ["life"] * min(2, game.player.lives)
    if game.player.lives > 2:
        lives_health.append("plus")
    if game.player.lives >= 0:
        lives_health += ["health"] * game.player.health

    x = 0
    for image in lives_health:
        screen.blit(image, (x, 450))
        x += IMAGE_WIDTH[image]

space_down = False

def space_pressed():
    global space_down
    if keyboard.space:
        if space_down:
            return False
        else:
            space_down = True
            return True

class State(Enum):
    MENU = 1
    PLAY = 2
    GAME_OVER = 3

def update():
    global state, game

    if state == State.MENU:
        if space_pressed():
            state = State.PLAY
            game = Game(Player())
        else:
            game.update()
        
    elif state == State.PLAY:
        if game.player.lives < 0:
            game.play_sound("over")
            state = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if space_pressed():
            state = State.MENU
            game = Game()

def draw():
    game.draw()

    if state == State.MENU:
        screen.blit("title", (0,0))
        anim_frame = min(((game.timer + 40) % 160) // 4, 9)
        screen.blit("space" + str(anim_frame), (130, 280))
        
    elif state == State.PLAY:
        draw_status()

    elif state == State.GAME_OVER:
        draw_status()
        screen.blit("over", (0,0))

pygame.mixer.quit()
pygame.mixer.init(44100, -16, 2, 1024)

music.play("theme")
music.set_volume(0.1)

state = State.MENU
game = Game()

#---------------------------------
from engine import run
run()
