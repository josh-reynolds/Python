import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((400,400))
running = True


s = pygame.Surface((80,20), flags=SRCALPHA)
#s.set_alpha(255)      # Ah! This is the issue!
s.fill((255,0,0))
s = pygame.transform.rotate(s, 15)

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_q:
                running = False

    screen.fill((0,0,255))
    screen.blit(s, (200-40,200-10))
    pygame.display.update()

pygame.quit()
