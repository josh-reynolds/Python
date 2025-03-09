import pygame
from engine import *

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

image_tester = Box((100,100))
image_tester.image = 'test'       # jpg image
image_tester.anchor = ('left','top')

image_tester2 = Box((600,100))
image_tester2.image = 'test2'      # gif image
image_tester2.anchor = ('left','top')

def update():
    for box in boxes:
        box.update()

    for k in dir(keys):
        if not k.startswith('__'):
            key = getattr(keys, k)
            if keyboard[key]:
                print(key)

def draw():
    screen.draw.line((0,0,255), (HALF_WIDTH,0), (HALF_WIDTH, HEIGHT))
    screen.draw.line((0,0,255), (0,HALF_HEIGHT), (WIDTH, HALF_HEIGHT))

    screen.draw.line((255,0,0), (0,100+16), (WIDTH,100+16))
    screen.draw.line((255,0,0), (0,300+16), (WIDTH,300+16))
    screen.draw.line((255,0,0), (100+16,0), (100+16,HEIGHT))
    screen.draw.line((255,0,0), (600+16,0), (600+16,HEIGHT))

    for box in boxes:
        box.draw()

    screen.draw.text("Lorem Ipsum Dolor Sit Amet", (20, 20))

    screen.draw.text("O", center=(HALF_WIDTH, 20))
    screen.draw.text("O", center=(20,HALF_HEIGHT))

    image_tester.draw()
    image_tester2.draw()

    screen.blit("image_1", (100,300))      # gif image
    screen.blit("image_2", (600,300))      # jpg image


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
    screen.draw.line((0,0,255), (HALF_WIDTH,0), (HALF_WIDTH, HEIGHT))
    screen.draw.line((0,0,255), (0,HALF_HEIGHT), (WIDTH, HALF_HEIGHT))

    b = Box((HALF_WIDTH, HALF_HEIGHT), anchor=('center','center'))
    b.update()
    b.draw()
    print_box(b)

run()
