from math import inf
from random import randint
import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((400,400))
running = True
counter = 0

A = [250,150]
B = [300,300]

C = [50,200]
D = [350,200]

def calc_slope_intercept(p1, p2):
    if p1[0] == p2[0]:
        return inf, inf
    slope = (p2[1] - p1[1])/(p2[0] - p1[0])
    intercept = p1[1] - slope * p1[0]
    return slope, intercept

def calc_intersection():
    m1, b1 = calc_slope_intercept(A, B)
    m2, b2 = calc_slope_intercept(C, D)

    if m1 != m2:
        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1
        return [x,y]
    return None        # parallel lines, no intersection

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_q:
                running = False

    if counter % 100 == 0:
        screen.fill(Color("white"))

        I = calc_intersection()

        pygame.draw.line(screen, Color("black"), A, B)
        pygame.draw.line(screen, Color("black"), C, D)
        if I:
            pygame.draw.circle(screen, Color("red"), I, 4)
        pygame.display.update()

        B[0] += randint(-1,1)
        B[1] += randint(-1,1)

        D[0] += randint(-1,1)
        D[1] += randint(-1,1)

    counter += 1


pygame.quit()

# extending lines to screen edges
# if abs(slope) > 1:
#     find point where y = 0
#     if 0 < point.x < width:
#         point is on top edge
#     if point.x < 0:
#         point is on left edge, find y
#     if point.x > width:
#         point is on right edge, find y
# else:
#     find point where :wq

