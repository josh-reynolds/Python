import math
from random import uniform, randint, random, choice
import pygame
from pygame import Rect, Surface, transform
from pygame.locals import *
from engine import *
from mover import Mover
from pvector import PVector
from liquid import Liquid
from attractor import Attractor, Repulsor
from rotator import Rotator
from orbiter import Orbiter
from oscillator import Oscillator
from wave import Wave
from pendulum import Pendulum
from spring import Spring
from particles import ParticleSystem, Particle, Smoke
from vehicle import Vehicle
from grid import Grid
from flow_field import FlowField
from path import Path
from boids import Boid
from flock import Flock
from wolfram import CA
from life import Life
from fractals import draw_circle, cantor, KochCurve, branch
from rotation_test import Test
from screen_matrix import sm, line, translate, rotate, push_matrix, pop_matrix
from lsystem import Rule, LSystem, Turtle

WIDTH = 640
HEIGHT = 480
TITLE = "The Nature of Code"

class Population:
    def __init__(self, mutation_rate, size):
        self.mutation_rate = mutation_rate
        self.population = [Rocket() for i in range(size)]
        self.mating_pool = []
        self.generations = 0

    def live(self):
        for p in self.population:
            p.run()

    def fitness(self):
        for p in self.population:
            p.calculate_fitness()

    def selection(self):
        self.mating_pool = []
        for p in self.population:
            n = int(p.fitness * 100)
            for i in range(n):
                self.mating_pool.append(p)

        if len(self.mating_pool) == 0:
            self.mating_pool = self.population.copy()
            print("zero pool")

    def reproduction(self):
        for i in range(len(self.population)):
            parent_a = choice(self.mating_pool)
            parent_b = choice(self.mating_pool)

            child = parent_a.crossover(parent_b)
            child.mutate(self.mutation_rate)

            self.population[i] = child

    def draw(self):
        for p in self.population:
            p.draw()

class Obstacle:
    def __init__(self, x, y, w, h):
        self.location = PVector(x,y)
        self.width = w
        self.height = h

    def contains(self, v):
        if (v.x > self.location.x and v.x < self.location.x + self.width and
            v.y > self.location.y and v.y < self.location.y + self.height):
            return True
        else:
            return False

    def draw(self):
        screen.draw.rect((self.location.x, self.location.y, self.width, self.height), (0,0,255), 0)

class Rocket:
    def __init__(self):
        self.dna = DNA()
        self.fitness = 0
        self.gene_counter = 0

        self.mass = 1
        self.location = PVector(WIDTH//2, HEIGHT)
        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)

        self.stopped = False

    def calculate_fitness(self):
        self.fitness = self.dna.fitness(self.location, self.stopped)

    def crossover(self, partner):
        child = Rocket()
        child.dna = self.dna.crossover(partner.dna)
        return child

    def mutate(self, mutation_rate):
        self.dna.mutate(mutation_rate)

    def run(self):
        if not self.stopped:
            self.apply_force(self.dna.genes[self.gene_counter])
            self.gene_counter += 1
            self.gene_counter %= lifetime
            self.update()
            self.collision_check()

    def apply_force(self, f):
        self.acceleration + f

    def update(self):
        self.velocity + self.acceleration
        self.location + self.velocity
        self.acceleration * 0

    def collision_check(self):
        for o in obstacles:
            if o.contains(self.location):
                self.stopped = True

    def draw(self):
        screen.draw.circle(self.location.x, self.location.y, self.mass * 16, (0, 255, 0))
        screen.draw.circle(self.location.x, self.location.y, self.mass * 16, (0, 0, 0), 1)

class DNA:
    def __init__(self):
        self.max_force = 0.1
        self.genes = []
        for i in range(lifetime):
            vec = PVector.random2D()
            vec * (uniform(0, self.max_force))
            self.genes.append(vec)

    def fitness(self, location, stopped):
        d = PVector.dist(location, target)
        #return (1 / d) ** 2
        f = 1/2
        if stopped:
            f *= 0.1
        return f

    def crossover(self, partner):
        child = DNA()
        midpoint = randint(0,len(child.genes))
        for i in range(len(child.genes)):
            if i > midpoint:
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = partner.genes[i]
        return child

    def mutate(self, mutation_rate):
        for i in range(len(self.genes)):
            if random() < mutation_rate:
                vec = PVector.random2D()
                vec * (uniform(0, self.max_force))
                self.genes[i] = vec

# ----------------------------------------------------
def update():
    global life_counter, generation

    if life_counter < lifetime:
        population.live()
        life_counter += 1
    else:
        life_counter = 0
        population.fitness()
        population.selection()
        population.reproduction()
        generation += 1
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    population.draw()
    for o in obstacles:
        o.draw()
    screen.draw.circle(target.x, target.y, 8, (255, 0, 0))
    screen.draw.text("Generation: " + str(generation), pos=(WIDTH - 140, 20))
    screen.draw.text("Cycle: " + str(life_counter), pos=(WIDTH - 140, 40))
# ----------------------------------------------------

# ----------------------------------------------------
def setup():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
lifetime = 500
life_counter = 0
population = Population(0.01, 100)
target = PVector(WIDTH//2, HEIGHT//3)
obstacles = [Obstacle(WIDTH//4, HEIGHT//2, WIDTH//2, 20)]
generation = 1

run()
# ----------------------------------------------------

# The primary difference from text: Processing does not redraw the background 
# automatically, but the engine does, so we aren't getting trails drawn 
# on-screen - consider implementing similar functionality

# Processing also expects a setup() function to be run once at the start - I toyed with
# this idea in the engine, but the top-level code just above the call to run() is 
# equivalent. If I _do_ add such a thing back to the engine, would need to use some
# trickery to avoid having to add a dummy setup() to old projects - we want backward
# compatibility.

# Latest hurdle: Processing includes a noise() function to generate Perlin noise. I don't
# have the equivalent in Pygame or stock Python. I _could_ import a module, but I am
# contemplating rolling my own and sticking into the engine. Researching now.

# Perlin noise project is working, need to package it up and add to the engine...

# Moving ahead to Chapter 1 now. New issue: the engine can't access top-level primitive 
# variables - or at least it can't modify them. But if we wrap the values in a class, it
# works fine. I think this is a referencing problem due to the way the engine finds the
# content of this parent script, need to fiddlw with this to sort it out. But for now,
# going ahead with class-based solution, which is why Example 1.1 above looks a little
# different from the book version. (Update - declaring as global in the function may do
# the trick...)

# Another potential addition to the engine: mouse support...

# The Processing transform functions are also handy. Don't have a good equivalent in
# Pygame. Could do something like it by:
#  1) drawing everything to a separate surface, not directly on the screen
#  2) applying the current 'screen transform' - defaulting to identity
#  3) blit the transformed surface to the screen surface
# translate(), rotate() etc. would modify the screen transform
# and then we'd want to also support push_matrix() and pop_matrix()
# fairly big change to the engine, with potential to break backwards compat, so need
# to approach carefully and test everything thoroughly

# Chapter 5 covers physics libraries. Apparently there _is_ a version of Box2D for pygame
# (pybox2d), and it seems to be available on NixOS according to the search page. But the 
# available versions are for Python 3.12 and 3.13, while I currently have 3.11. Some
# fiddling required. The story with toxiclibs is murkier. But a general search for 
# 'pygame physics libraries' turns up pymunk, so may give that one a go.

# In the meantime, I think I'll skip over Chapter 5 and revisit it later.

# Rotation was an issue again in the Fractal chapter (8). I implemented a rotate on my
# homegrown vector class, and a test class to verify everything is working OK. May still be
# some weirdness going on as compared to the Processing equivalent. Radians vs. degrees in
# the various function calls is easy to get crossed up. Behavior in all four quadrants, 
# rotational direction, and going past 360 degrees are all consderations too. But this is
# working well enough to get the Koch curve implemented.

# I've been able to survive without push/popmatrix so far, but the next section on Fractal
# Trees makes heavy use of it. Will need to think about an approach. As noted above, the
# long-term solution is probably to integrate this deeply into the engine, but that's more
# work than warranted just yet. But maybe a tiny class that wraps calls to screen.draw could
# give the desired behavior.

# What if screen retains the matrix settings? So you'd call screen.translate(), screen.rotate(),
# etc. It would maintain a transform matrix, which may be enough on its own. Translate by itself
# could be handled just by an 'origin' field, which by default is set to the top-left of the
# window (0,0).

# Additional hurdle to add into this one: the transform calls should be relative/accumulative,
# but the current model has us calling repeatedly in draw() - and we need to do that because
# otherwise the first draw() out of the run() loop will clear the screen. So... I'm adding
# back the setup() function with a hook in the main loop (I previously called this 'once()'). As
# noted above, we'll need to do something dynamic to preserve backward compatibility (i.e. don't
# barf if the main script does not have a setup() function.

# I also needed to suppress the auto-fill behavior in the main loop, via an optional flag to
# run(). This is a bit klunky right now, needs lots of smoothing before we can bring it back
# to the main engine project. But this is a good sandbox for figuring it all out.
