import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((400,400))
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_q:
                running = False

    screen.fill((0,0,255))
    pygame.display.update()

pygame.quit()
