# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *
from common import *

rect = Rect(50, 60, 200, 80)
rects = random_rects(100)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_r:
                rects = random_rects(100)

    screen.fill(GREY)
    pygame.draw.rect(screen, GREEN, rect, 1)

    for r in rects:
        if rect.colliderect(r):
            pygame.draw.rect(screen, RED, r, 2)
        else:
            pygame.draw.rect(screen, BLUE, r, 1)

    pygame.display.flip()

pygame.quit()


