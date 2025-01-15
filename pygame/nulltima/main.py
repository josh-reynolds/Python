import pygame
from pygame.locals import *
from common import *
from grid import grid

g = grid(11, 11, 60, 60, 32, 32)
#g.world.open_file("test_world.txt")
g.world.open_file("large_world.txt")

def draw_text(text, pos):
    img = font.render(text, True, BLACK)
    screen.blit(img, pos)

pygame.init()
screen = pygame.display.set_mode(SIZE)
font = pygame.font.Font(None, 24)

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
    draw_text("Arrow keys to move", (420, 60))
    draw_text("q to quit", (420, 80))
    pygame.display.flip()

pygame.quit()
