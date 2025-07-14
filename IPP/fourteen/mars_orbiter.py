"""Game simulating satellite orbiting Mars."""
#import os
import math
import random
import pygame as pg
# pylint: disable=C0103, R0902

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
LT_BLUE = (173,216,230)

class Satellite(pg.sprite.Sprite):
    """Satellite object that rotates to face planet & crashes & burns."""

    def __init__(self, background):
        """Create a Satellite."""
        super().__init__()
        self.background = background
        self.image_sat = pg.image.load('satellite.png').convert()
        self.image_crash = pg.image.load('satellite_crash_40x33.png').convert()
        self.image = self.image_sat
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)

        self.x = random.randrange(315, 425)
        self.y = random.randrange(70, 180)
        self.dx = random.choice([-3, 3])
        self.dy = 0
        self.heading = 0
        self.fuel = 100
        self.mass = 1
        self.distance = 0
        self.thrust = pg.mixer.Sound('trust_audio.ogg')
        self.thrust.set_volume(0.07)

    def thruster(self, dx, dy):
        """Execute actions assocated with firing thrusters."""
        self.dx += dx
        self.dy += dy
        self.fuel -= 2
        self.thrust.play()

    def check_keys(self):
        """Check if user presses arrow keys & call thruster() method."""
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            self.thruster(dx=0.05, dy=0)
        elif keys[pg.K_LEFT]:
            self.thruster(dx=-0.05, dy=0)
        elif keys[pg.K_UP]:
            self.thruster(dx=0, dy=-0.05)
        elif keys[pg.K_DOWN]:
            self.thruster(dx=0, dy=0.05)

    def locate(self, planet):
        """Calculate distance & heading to planet."""
        px, py = planet.x, planet.y
        dist_x = self.x - px
        dist_y = self.y - py
        planet_dir_radians = math.atan2(dist_x, dist_y)
        self.heading = planet_dir_radians * 180 / math.pi
        self.heading -= 90
        self.distance = math.hypot(dist_x, dist_y)

    def rotate(self):
        """Rotate satellite using degrees so dish faces planet."""
        self.image = pg.transform.rotate(self.image_sat, self.heading)
        self.rect = self.image.get_rect()

    def path(self):
        """Update satellite's position & draw line to trace orbital path."""
        last_center = (self.x, self.y)
        self.x += self.dx
        self.y += self.dy
        pg.draw.line(self.background, WHITE, last_center, (self.x, self.y))

    def update(self):
        """Update satellite object dring game."""
        self.check_keys()
        self.rotate()
        self.path()
        self.rect.center = (self.x, self.y)
        if self.dx == 0 and self.dy == 0:
            self.image = self.image_crash
            self.image.set_colorkey(BLACK)

class Planet(pg.sprite.Sprite):
    """Planet object that rotates & projects gravity field."""

    def __init__(self):
        """Create a Planet."""
        super().__init__()
        self.image_mars = pg.image.load("mars.png").convert()
        self.image_water = pg.image.load("mars_water.png").convert()
        self.image_copy = pg.transform.scale(self.image_mars, (100,100))
        self.image_copy.set_colorkey(BLACK)
        self.rect = self.image_copy.get_rect()
        self.image = self.image_copy
        self.mass = 2000
        self.x = 400
        self.y = 320
        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.01)

    def rotate(self):
        """Rotate the planet image with each game loop."""
        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by

    def gravity(self, satellite):
        """Calculate impact of gravity on satellite."""
        G = 1.0
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y
        distance = math.hypot(dist_x, dist_y)
        dist_x /= distance
        dist_y /= distance
        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)

    def update(self):
        """Call the rotate method."""
        self.rotate()
