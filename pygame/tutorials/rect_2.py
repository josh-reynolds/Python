# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *

RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)
GREY   = (150, 150, 150)
BLACK  = (  0,   0,   0)
SIZE   = (500, 200)

width, height = SIZE
dirs = {K_LEFT: (-5, 0), K_RIGHT: (5, 0), K_UP: (0, -5), K_DOWN: (0, 5)}

pygame.init()
screen = pygame.display.set_mode(SIZE)

rect0 = Rect(50, 60, 200, 80)
rect = rect0.copy()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_l:
                rect.left = 0
            if event.key == K_c:
                rect.centerx = width//2
            if event.key == K_r:
                rect.right = width
            if event.key == K_t:
                rect.top = 0
            if event.key == K_m:
                rect.centery = height//2
            if event.key == K_b:
                rect.bottom = height
            if event.key in dirs:
                v = dirs[event.key]
                rect.move_ip(v)

    screen.fill(GREY)
    pygame.draw.rect(screen, BLUE, rect0, 1)
    pygame.draw.rect(screen, RED, rect, 4)
    pygame.display.flip()

pygame.quit()


