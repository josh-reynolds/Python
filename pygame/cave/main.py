import sys
from random import choice, randint, random, shuffle
from enum import Enum
import pygame
from engine import Actor

if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

WIDTH = 800
HEIGHT = 480
TITLE = "Cave"








def update():
    pass

def draw():
    pass

#---------------------------------
from engine import run
run()
