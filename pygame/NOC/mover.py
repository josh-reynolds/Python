import pygame
from engine import *
from pvector import PVector

class Mover:
    def __init__(self, m, x, y, WIDTH, HEIGHT):
        self.max_width = WIDTH
        self.max_height = HEIGHT
        self.mass = m
        self.location = PVector(x, y)
        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)
        self.top_speed = 10

    def update(self):
        self.velocity + self.acceleration
        self.velocity.limit(self.top_speed)
        self.location + self.velocity
        self.check_edges()
        self.acceleration * 0

    def check_edges(self):
        if self.location.x > self.max_width:
            self.location.x = self.max_width
            self.velocity.x *= -1
        elif self.location.x < 0:
            self.location.x = 0
            self.velocity.x *= -1

        if self.location.y > self.max_height:
            self.location.y = self.max_height
            self.velocity.y *= -1
        elif self.location.y < 0:
            self.location.y = 0
            self.velocity.y *= -1

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, self.mass*16, (255,0,0))
        screen.draw.circle(self.location.x, self.location.y, self.mass*16, (0,0,0), 1)

    def apply_force(self, force):
        f = PVector.div(force, self.mass)
        self.acceleration + f

    def is_inside(self, liquid):
        return liquid.rect.collidepoint(self.location.x, self.location.y)

    def drag(self, liquid):
        speed = self.velocity.mag()
        dragMagnitude = liquid.c * speed * speed

        drag = self.velocity.mult(-1).normalize()
        drag * dragMagnitude
        self.apply_force(drag)
