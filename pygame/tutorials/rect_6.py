# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *
from common import *

rect = Rect(50, 60, 200, 80)
points = random_points(100)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_r:
                points = random_points(100)


    screen.fill(GREY)
    pygame.draw.rect(screen, GREEN, rect, 1)
    for point in points:
        if rect.collidepoint(point):
            pygame.draw.circle(screen, RED, point, 4, 0)
        else:
            pygame.draw.circle(screen, BLUE, point, 4, 0)
    pygame.display.flip()

pygame.quit()


