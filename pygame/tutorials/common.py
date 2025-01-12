import pygame
from random import randint

RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
LT_GRN  = (150, 255, 150)
BLUE    = (  0,   0, 255)
CYAN    = (  0, 255, 255)
MAGENTA = (255,   0, 255)
YELLOW  = (255, 255,   0)
WHITE   = (255, 255, 255)
GREY    = (150, 150, 150)
BLACK   = (  0,   0,   0)

SIZE   = (500, 200)

width, height = SIZE

def draw_text(text, pos):
    img = font.render(text, True, BLACK)
    screen.blit(img, pos)

def random_point():
    x = randint(0, width)
    y = randint(0, height)
    return (x, y)

def random_points(n):
    points = []
    for i in range(n):
        p = random_point()
        points.append(p)
    return points

def random_rects(n):
    rects = []
    for i in range(n):
        r = pygame.Rect(random_point(), (20, 20))
        rects.append(r)
    return rects

pygame.init()
screen = pygame.display.set_mode(SIZE)
font = pygame.font.Font(None, 24)
