import pygame
from engine import Actor, music, keyboard, sounds

WIDTH = 800
HEIGHT = 480
TITLE = "Test Bed"

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

class Box(Actor):
    def __init__(self, pos, anchor=('center','center')):
        super().__init__("blank", pos, anchor)

    def update(self):
        self.image = "box"

    def __repr__(self):
        return f"Box({self.pos})"

xs = ('left', 'center', 'right')
ys = ('top', 'center', 'bottom')
boxes = [Box((HALF_WIDTH, HALF_HEIGHT), anchor=(x,y)) for x in xs for y in ys]

def update():
    for box in boxes:
        box.update()
    #pass

def draw():
    screen.draw_line((0,0,255), (HALF_WIDTH,0), (HALF_WIDTH, HEIGHT))
    screen.draw_line((0,0,255), (0,HALF_HEIGHT), (WIDTH, HALF_HEIGHT))
    for box in boxes:
        box.draw()
    pass

def print_box(b):
    print(f'screen center = {HALF_WIDTH}, {HALF_HEIGHT}')
    print(f'box = {b}')
    print(f'box rect = {b.rect}')
    print(f'box anchor = {b.anchor}')
    print(f'box image = {b.image}')
    print(f'box image rect = {b.image.get_rect()}')
    print(f'box rect topleft = {b.rect.topleft}')
    print(f'box rect left = {b.rect.left}')
    print(f'box rect top = {b.rect.top}')
    
def once():
    screen.draw_line((0,0,255), (HALF_WIDTH,0), (HALF_WIDTH, HEIGHT))
    screen.draw_line((0,0,255), (0,HALF_HEIGHT), (WIDTH, HALF_HEIGHT))

    b = Box((HALF_WIDTH, HALF_HEIGHT), anchor=('center','center'))
    b.update()
    b.draw()
    print_box(b)

    #pygame.quit()

from engine import run
run()
