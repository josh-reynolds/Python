import pygame
from pygame.locals import *
from common import *
from grid import grid

g = grid(3, 3, 60, 60, 50, 50)
g.world.contents = [[1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 4, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1]]

pygame.init()
screen = pygame.display.set_mode(SIZE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill(GREY)
    g.update()
    g.draw(screen)
    pygame.display.flip()

pygame.quit()
