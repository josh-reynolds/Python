"""Simulate Tvashtar eruption on Io."""
#import sys
import math
import random
import pygame as pg

pg.init()

BLACK = (0,0,0)
WHITE = (255,255,255)
LT_GRAY = (180,180,180)
GRAY = (120,120,120)
DK_GRAY = (80,80,80)

class Particle(pg.sprite.Sprite):
    """Builds ejecta particles for volcano simulation."""

    gases_colors = {'SO2': LT_GRAY, 'CO2': GRAY, 'H2S': DK_GRAY, 'H2O': WHITE}

    VENT_LOCATION_XY = (320,300)
    IO_SURFACE_Y = 308
    GRAVITY = 0.5
    VELOCITY_SO2 = 8

    vel_scalar = {'SO2': 1, 'CO2': 1.45, 'H2S': 1.9, 'H2O': 3.6}

    def __init__(self, screen, background):
        """Create a Particle."""
        super().__init__()
        self.screen = screen
        self.background = background
        self.image = pg.Surface((4,4))
        self.rect = self.image.get_rect()
        self.gas = random.choice(list(Particle.gases_colors.keys()))
        self.color = Particle.gases_colors[self.gas]
        self.vel = Particle.VELOCITY_SO2 * Particle.vel_scalar[self.gas]
        self.x, self.y = Particle.VENT_LOCATION_XY
        self.vector()

    def vector(self):
        """Calculate particle vector at launch."""
        orient = random.uniform(60,120)
        radians = math.radians(orient)
        self.dx = self.vel * math.cos(radians)
        self.dy = -self.vel * math.sin(radians)

def main():
    """Run the simulation."""

if __name__ == '__main__':
    main()
