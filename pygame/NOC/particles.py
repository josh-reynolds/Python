from random import uniform, random, randint
from pygame.locals import *
from pvector import PVector
from engine import *

class ParticleSystem:
    def __init__(self, x, y):
        self.particles = []
        self.origin = PVector(x,y)
        self.gravity = PVector(0, 0.1)

    def add_particle(self):
        if random() < 0.8: 
            self.particles.append(Particle(self.origin.x, self.origin.y))
        else:
            self.particles.append(Confetti(self.origin.x, self.origin.y))

    def update(self):
        self.apply_force(self.gravity)
        for p in self.particles:
            p.update()
            if p.is_dead():
                self.particles.remove(p)

    def draw(self):
        for p in self.particles:
            p.draw()

    def random_walk(self):
        self.origin.x += (uniform(-5,5))
        self.origin.y += (uniform(-5,5))

    def apply_force(self, force):
        for p in self.particles:
            p.apply_force(force)

    def apply_repulsor(self, repulsor):
        for p in self.particles:
            force = repulsor.attract(p)
            p.apply_force(force)

class Particle:
    def __init__(self, x, y):
        self.location = PVector(x,y)
        self.acceleration = PVector(0,0)
        self.velocity = PVector(uniform(-1,1), uniform(-2,0))
        self.lifespan = 255
        self.mass = 1

    def update(self):
        self.velocity + self.acceleration
        self.location + self.velocity
        self.acceleration * 0
        self.lifespan -= 2

    def draw(self):
        # TO_DO: add alpha support to Painter.circle()
        if self.lifespan >= 0:
            screen.draw.circle(self.location.x, self.location.y, 8, (255,64,64,self.lifespan))
            screen.draw.circle(self.location.x, self.location.y, 8, (0,0,0,self.lifespan), 1)

    def is_dead(self):
        return self.lifespan < 0.0

    def apply_force(self, force):
        f = PVector.div(force, self.mass)
        self.acceleration + f

# book example uses rotation, but my current implementation is a hassle to set up
# will try a random size and different color instead to distinguish... the example
# is really about inheritance/polymorphism anyway
# TO_DO: simplify rotation
class Confetti(Particle):
    def __init__(self, x, y):
        self.size = randint(2,20)
        super().__init__(x, y)

    def draw(self):
        if self.lifespan >= 0:
            screen.draw.circle(self.location.x, self.location.y, self.size, (0,255,0,self.lifespan))
            screen.draw.circle(self.location.x, self.location.y, self.size, (0,0,0,self.lifespan), 1)

class SmokeParticle(Particle):
    def __init__(self, x, y):
        self.image = images.texture_2
        super().__init__(x,y)
        self.velocity = PVector(uniform(-1.0,1.0)*0.7, random()*0.3-1.0)

    def draw(self):
        if self.lifespan >= 0:
            self.image.set_alpha(self.lifespan//2)
            screen.blit(self.image, (self.location.x, self.location.y), special_flags=BLEND_RGBA_ADD)

class Smoke(ParticleSystem):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.gravity = PVector(0,-0.01)

    def add_particle(self):
        self.particles.append(SmokeParticle(self.origin.x, self.origin.y))
