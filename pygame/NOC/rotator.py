import pygame
from pygame import Rect, Surface, transform
from pygame.locals import SRCALPHA
from engine import *

class Rotator:
    def __init__(self, x, y, a_vel):
        self.x = x
        self.y = y
        self.rect = Rect(x, y, 80, 20)
        self.color = (0, 200, 0)

        width, height = self.rect.size
        radius = height//2
        self.surf = Surface((self.rect.width, self.rect.height), flags=SRCALPHA)

        pygame.draw.line(self.surf, (0,0,0), (radius,radius), (width-radius,radius), width=2)
        pygame.draw.circle(self.surf, self.color, (radius, radius), radius)
        pygame.draw.circle(self.surf, (0,0,0), (radius, radius), radius, width=2)
        pygame.draw.circle(self.surf, self.color, (width-radius, radius), radius)
        pygame.draw.circle(self.surf, (0,0,0), (width-radius, radius), radius, width=2)

        self.original_surf = self.surf.copy()

        self.angle = 0
        self.a_vel = a_vel

    def update(self, a_acceleration):
        self.a_vel += a_acceleration
        self.angle += self.a_vel
        self.rotate()

    def draw(self):
        screen.blit(self.surf, (self.rect.x, self.rect.y))

    def rotate(self):
        self.surf = transform.rotate(self.original_surf, self.angle)
        w,h = self.surf.get_size()
        self.rect = Rect(self.x-w/2, self.y-h/2, w, h)

    def translate(self, dx, dy):
        self.x += dx
        self.y += dy
