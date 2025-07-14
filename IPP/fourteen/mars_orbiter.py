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
