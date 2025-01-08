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

start = (0,0)
size = (0,0)
drawing = False
rect_list = []

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            start = event.pos
            size = (0,0)
            drawing = True
        elif event.type == MOUSEBUTTONUP:
            end = event.pos
            size = end[0] - start[0], end[1] - start[1]
            rect = pygame.Rect(start, size)
            rect_list.append(rect)
            drawing = False
        elif event.type == MOUSEMOTION and drawing:
            end = event.pos
            size = end[0] - start[0], end[1] - start[1]

    screen.fill(background)

    for rect in rect_list:
        pygame.draw.rect(screen, RED, rect, 2)

    pygame.draw.rect(screen, BLUE, (start, size), 2)

    pygame.display.update()

pygame.quit()
