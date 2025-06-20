import math
from random import randint, random, uniform
from pvector import PVector
from engine import remap, screen

class World:
    def __init__(self, size, max_width, max_height):
        self.bloops = [Bloop(PVector(randint(0,max_width), 
                                     randint(0,max_height)), 
                                     DNA(), max_width, max_height) for i in range(size)]
        self.foods = [PVector(uniform(0,max_width), uniform(0,max_height)) for i in range(size*50)]

    def update(self):
        for b in self.bloops:
            b.update()
            b.eat(self.foods)
            child = b.reproduce()
            if child is not None:
                self.bloops.append(child)
        for i in range(len(self.bloops)-1,-1,-1):
            if self.bloops[i].is_dead():
                b = self.bloops[i]
                self.foods.append(PVector(b.location.x, b.location.y))
                self.bloops.remove(b)

    def draw(self):
        for b in self.bloops:
            b.draw()
        for f in self.foods:
            screen.draw.rect((f.x - 3, f.y - 3, 6, 6), (255,0,0), 0)

class DNA:
    def __init__(self):
        self.genes = [random()]

    def copy(self):
        d = DNA()
        d.genes = self.genes.copy()
        return d

    def mutate(self, mutation_rate):
        if random() < mutation_rate:
            self.genes = [random()]

class Bloop:
    def __init__(self, location, dna, max_width, max_height):
        self.location = location
        self.xoff = uniform(20.1,220.1)
        self.yoff = uniform(2.1,20.1)
        self.health = 100
        self.color = (randint(0,255), randint(0,255), randint(0,255))

        self.dirx = 1
        self.diry = 1

        self.dna = dna
        self.r = remap(self.dna.genes[0], 0, 1, 0, 50)
        self.max_speed = remap(self.dna.genes[0], 0, 1, 15, 0)

        self.max_width = max_width
        self.max_height = max_height

    def update(self):
        vx = remap(noise(self.xoff),-1,1,-self.max_speed,self.max_speed) * self.dirx
        vy = remap(noise(self.yoff),-1,1,-self.max_speed,self.max_speed) * self.diry
        velocity = PVector(vx,vy)
        self.xoff += 0.01
        self.yoff += 0.01

        self.location + velocity
        if self.location.x <= 0 or self.location.x >= self.max_width:
            self.dirx *= -1
        if self.location.y <= 0 or self.location.y >= self.max_width:
            self.diry *= -1

        self.health -= 1

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, self.r, self.color)
        screen.draw.circle(self.location.x, self.location.y, self.r, (0,0,0), 1)

    def is_dead(self):
        return self.health < 0.0

    def eat(self, foods):
        for f in foods:
            d = PVector.dist(self.location, f)
            if d < self.r:
                self.health += 100
                foods.remove(f)

    def reproduce(self):
        if random() < 0.01:
            dna = self.dna.copy()
            dna.mutate(0.01)
            return Bloop(self.location, dna, self.max_width, self.max_height)
        else:
            return None

repeat = 128
scale = 0.01
#seed(100000)
gradients = [(1,1), (math.sqrt(2),0), (1,-1), (0,math.sqrt(2)),
             (0,-math.sqrt(2)), (-1,1), (-math.sqrt(2),0), (-1,1)]
random_values = [[randint(0,7) for i in range(repeat)] for i in range(repeat)]

def noise(offset):
    x = offset * scale
    y = 50.1 * scale

    x %= repeat
    y %= repeat

    # grid corners
    x1, y1 = int(x) % repeat, int(y) % repeat
    x2, y2 = (x1 + 1) % repeat, (y1 + 1) % repeat

    # distance vectors
    dA, dB, dC, dD = (x1 - x, y1 - y), \
                     (x1 - x, y2 - y), \
                     (x2 - x, y1 - y), \
                     (x2 - x, y2 - y)

    # gradient vectors
    gA, gB, gC, gD = gradients[random_values[x1][y1]], \
                     gradients[random_values[x1][y2]], \
                     gradients[random_values[x2][y1]], \
                     gradients[random_values[x2][y2]]

    # dot products
    dotA, dotB, dotC, dotD = (dA[0] * gA[0] + dA[1] * gA[1]), \
                             (dB[0] * gB[0] + dB[1] * gB[1]), \
                             (dC[0] * gC[0] + dC[1] * gC[1]), \
                             (dD[0] * gD[0] + dD[1] * gD[1])

    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    # fade values
    u, v = fade(x - x1), fade(y - y1)

    #interpolation
    tmp1 = u * dotC + (1 - u) * dotA  # top edge
    tmp2 = u * dotD + (1 - u) * dotB  # bottom edge
    return v * tmp2 + (1 - v) * tmp1  # vertical
