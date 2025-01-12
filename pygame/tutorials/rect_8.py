# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *
from common import *

n = 30
rects = random_rects(n)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_r:
                rects = random_rects(n)

    screen.fill(GREY)

    intersecting = []
    for i in range(n-1):
        r0 = rects[i]
        for j in range(i+1, n):
            r1 = rects[j]
            if r0.colliderect(r1):
                intersecting.append(r0)
                intersecting.append(r1)
                break

    for i, r in enumerate(rects):
        color = RED if r in intersecting else BLUE
        pygame.draw.rect(screen, color, r)
        draw_text(str(i), r.topleft)

    pygame.display.flip()

pygame.quit()


