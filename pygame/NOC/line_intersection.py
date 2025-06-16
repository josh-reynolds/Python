import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((400,400))
running = True

# as written does not protect against division by zero

# Line AB --------------------------
A = (250,150)
B = (300,300)

m1 = (B[1] - A[1])/(B[0] - A[0])
b1 = A[1] - m1 * A[0]

# Line CD --------------------------
C = (50,200)
D = (350,200)

m2 = (D[1] - C[1])/(D[0] - C[0])
b2 = C[1] - m2 * C[0]

# Intersection ---------------------
x = (b2 - b1) / (m1 - m2)
y = m1 * x + b1

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_q:
                running = False

    screen.fill(Color("white"))
    pygame.draw.line(screen, Color("black"), A, B)
    pygame.draw.line(screen, Color("black"), C, D)
    pygame.draw.circle(screen, Color("red"), (x,y), 4)
    pygame.display.update()

pygame.quit()
