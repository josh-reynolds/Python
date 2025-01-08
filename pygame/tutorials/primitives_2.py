# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *

RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
GREY   = (128, 128, 128)
BLUE   = (  0,   0, 255)

background = GREY
size = 640, 320
width, height = size

pygame.init()
screen = pygame.display.set_mode(size)
running = True

drawing = False
points = []

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            points.append(event.pos)
            drawing = True
        elif event.type == MOUSEBUTTONUP:
            drawing = False
        elif event.type == MOUSEMOTION and drawing:
            points[-1] = event.pos
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if len(points) > 0:
                    points.pop()

    screen.fill(background)

    if len(points) > 1:
        rect = pygame.draw.lines(screen, RED, True, points, 3)
        pygame.draw.rect(screen, GREEN, rect, 1)

    pygame.display.update()

pygame.quit()
