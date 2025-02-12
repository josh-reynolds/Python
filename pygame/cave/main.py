import sys
from random import choice, randint, random, shuffle
from enum import Enum
import pygame
from engine import Actor, music

if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

WIDTH = 800
HEIGHT = 480
TITLE = "Cave"


class Game():
    def __init__(self):
        self.timer = 0

    def update(self):
        pass
    
    def draw(self):
        pass

def space_pressed():
    pass

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
