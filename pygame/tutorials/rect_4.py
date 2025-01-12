# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *
from common import *

dirs = {K_LEFT: (-5, 0), K_RIGHT: (5, 0), K_UP: (0, -5), K_DOWN: (0, 5)}
rect1 = Rect(50, 60, 200, 80)
rect2 = rect1.copy()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_l:
                rect2.left = 0
            if event.key == K_c:
                rect2.centerx = width//2
            if event.key == K_r:
                rect2.right = width
            if event.key == K_t:
                rect2.top = 0
            if event.key == K_m:
                rect2.centery = height//2
            if event.key == K_b:
                rect2.bottom = height
            if event.key in dirs:
                v = dirs[event.key]
                rect2.move_ip(v)

    clip = rect1.clip(rect2)
    union = rect1.union(rect2)

    screen.fill(GREY)
    pygame.draw.rect(screen, YELLOW, union, 0)
    pygame.draw.rect(screen, GREEN, clip, 0)
    pygame.draw.rect(screen, BLUE, rect1, 1)
    pygame.draw.rect(screen, RED, rect2, 4)
    pygame.display.flip()

pygame.quit()


