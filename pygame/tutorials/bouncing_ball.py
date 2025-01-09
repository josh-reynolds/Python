# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *
from common import *

ball = pygame.image.load("ball.gif")
rect = ball.get_rect()
speed = [1, 1]
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    rect = rect.move(speed)
    if rect.left < 0 or rect.right > width:
        speed[0] = -speed[0]
    if rect.top < 0 or rect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(LT_GRN)
    screen.blit(ball, rect)
    pygame.display.update()
    clock.tick(120)

pygame.quit()
