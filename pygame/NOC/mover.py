import pygame
from random import randrange
from engine import *
from pvector import PVector

class Mover:
    def __init__(self, max_width, max_height):
        self.max_width = max_width
        self.max_height = max_height
        self.location = PVector(randrange(max_width), randrange(max_height))
        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)
        self.top_speed = 10

    def update(self):
        mouse = PVector(*pygame.mouse.get_pos())
        direction = PVector.sub(mouse, self.location).normalize()
        direction * 0.5
        self.acceleration = direction

        self.velocity + self.acceleration
        self.velocity.limit(self.top_speed)
        self.location + self.velocity
        self.check_edges()

    def check_edges(self):
        if self.location.x > self.max_width:
            self.location.x = 0
        elif self.location.x < 0:
            self.location.x = self.max_width

        if self.location.y > self.max_height:
            self.location.y = 0
        elif self.location.y < 0:
            self.location.y = self.max_height

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, 10, (255,0,0))
