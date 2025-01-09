# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *
from common import *

rect = Rect(50, 60, 200, 80)
print(f'x={rect.x}, y={rect.y}, w={rect.w}, h={rect.h}')
print(f'left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}')
print(f'center={rect.center}')

pts = ('topleft', 'topright', 'bottomleft', 'bottomright',
       'midleft', 'midright', 'midtop', 'midbottom', 'center')

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill(GREY)
    pygame.draw.rect(screen, GREEN, rect, 2)
    for pt in pts:
        pos = eval('rect.'+pt)
        draw_text(pt, pos)
        pygame.draw.circle(screen, RED, pos, 3)

    pygame.display.flip()

pygame.quit()


