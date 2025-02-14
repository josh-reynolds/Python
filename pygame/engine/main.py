import pygame
from engine import Actor, music, keyboard, sounds

WIDTH = 800
HEIGHT = 480
TITLE = "Test Bed"

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

class Box(Actor):
    def __init__(self, pos, anchor=('center','center')):
        super().__init__("box", pos, anchor)

    def update(self):
        pass

    def __repr__(self):
        return f"Box({self.pos})"

xs = ('left', 'center', 'right')
ys = ('top', 'center', 'bottom')
boxes = [Box((HALF_WIDTH, HALF_HEIGHT), anchor=(x,y)) for x in xs for y in ys]

def update():
    for box in boxes:
        box.update()

def draw():
    screen.draw_line((0,0,255), (HALF_WIDTH,0), (HALF_WIDTH, HEIGHT))
    screen.draw_line((0,0,255), (0,HALF_HEIGHT), (WIDTH, HALF_HEIGHT))
    for box in boxes:
        box.draw()

from engine import run
run()
