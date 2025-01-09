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

pygame.init()
screen = pygame.display.set_mode(SIZE)

rect = Rect(50, 60, 200, 80)

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

    screen.fill(GREY)
    pygame.draw.rect(screen, BLUE, rect)
    pygame.display.flip()

pygame.quit()


