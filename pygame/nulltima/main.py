import pygame
from pygame.locals import *
from common import *
from grid import grid

g = grid(3,3)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill(GREY)
    pygame.display.flip()

pygame.quit()
