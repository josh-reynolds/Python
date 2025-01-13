import pygame
from pygame.locals import *

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
BROWN   = ( 65,  17,  17)

SIZE   = (640, 480)

width, height = SIZE
dirs = {K_LEFT: (-1, 0), K_RIGHT: (1, 0), K_UP: (0, -1), K_DOWN: (0, 1)}

def draw_text(text, pos):
    img = font.render(text, True, BLACK)
    screen.blit(img, pos)

