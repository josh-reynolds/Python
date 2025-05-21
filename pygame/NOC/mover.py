import pygame
from pygame import Rect, Surface, transform
from pygame.locals import *
from engine import *
from pvector import PVector

class Mover:
    def __init__(self, m, x, y, WIDTH, HEIGHT):
        self.max_width = WIDTH
        self.max_height = HEIGHT
        
        self.location = PVector(x, y)
        self.rect = Rect(x, y, 20, 80)
        self.color = (0, 200, 0)

        width,height = self.rect.size
        self.surf = Surface((self.rect.width, self.rect.height), flags=SRCALPHA)
        pygame.draw.rect(self.surf, self.color, (0, 0, width, height), width=0) 
        pygame.draw.rect(self.surf, (0,0,0), (0, 0, width, height), width=1) 
        pygame.draw.circle(self.surf, (0,0,0), (10,70), 10, 0)
        self.original_surf = self.surf.copy()

        self.mass = m
        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)
        self.top_speed = 10
        self.G = 0.4

        self.angle = 0
        self.a_vel = 0
        self.a_accel = 0

    def update(self):
        self.velocity + self.acceleration
        self.velocity.limit(self.top_speed)
        self.location + self.velocity

        #self.a_accel = self.acceleration.x / 10
        #self.a_vel += self.a_accel
        #self.a_vel = max(min(self.a_vel, 0.1), -0.1)
        #self.angle += self.a_vel
        self.angle = self.velocity.heading()
        self.rotate()

        self.check_edges()
        self.acceleration * 0

    def check_edges(self):
        if self.location.x > self.max_width:
            #self.location.x = self.max_width
            #self.velocity.x *= -1
            self.location.x = 0
        elif self.location.x < 0:
            #self.location.x = 0
            #self.velocity.x *= -1
            self.location.x = self.max_width

        if self.location.y > self.max_height:
            #self.location.y = self.max_height
            #self.velocity.y *= -1
            self.location.y = 0
        elif self.location.y < 0:
            #self.location.y = 0
            #self.velocity.y *= -1
            self.location.y = self.max_height

    def draw(self):
        #screen.draw.circle(self.location.x, self.location.y, self.mass*16, (255,0,0))
        #screen.draw.circle(self.location.x, self.location.y, self.mass*16, (0,0,0), 1)
        screen.blit(self.surf, (self.rect.x, self.rect.y))

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

    def attract(self, mover):
        force = PVector.sub(self.location, mover.location)
        distance = force.mag()
        distance = max(min(distance, 25), 5)
        force.normalize()
        strength = (self.G * self.mass * mover.mass) / (distance * distance)
        force * strength
        return force

    def rotate(self):
        self.surf = transform.rotate(self.original_surf, self.angle)
        w,h = self.surf.get_size()
        self.rect = Rect(self.location.x-w/2, self.location.y-h/2, w, h)
