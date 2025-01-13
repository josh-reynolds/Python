import pygame
from pygame.locals import *
from common import *
from grid import grid

g = grid(11, 11, 60, 60, 25, 25)
#g.world.open_file("test_world.txt")
g.world.open_file("large_world.txt")

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
            elif event.key == K_q:
                running = False

    screen.fill(GREY)
    g.update()
    g.draw(screen)
    pygame.display.flip()

pygame.quit()
