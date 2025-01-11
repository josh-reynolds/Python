import pygame
from pygame.locals import *
from common import *
from grid import grid

g = grid(3, 3, 60, 60, 50, 50)
g.world.contents = [[0, 0, 0, 0, 0],
                    [0, 1, 1, 3, 0],
                    [0, 1, 4, 1, 0],
                    [0, 3, 1, 1, 0],
                    [0, 0, 0, 0, 0]]
g.offset = (1,1)

pygame.init()
screen = pygame.display.set_mode(SIZE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key in dirs:
                v = dirs[event.key]
                g.move(v[0], v[1])

    screen.fill(GREY)
    g.update()
    g.draw(screen)
    pygame.display.flip()

pygame.quit()
