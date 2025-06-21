import math
from random import uniform, randint, random, choice, seed
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
from rocket import SmartRockets
from face import Faces
from ecosystem import World

WIDTH = 640
HEIGHT = 480
TITLE = "The Nature of Code"

class Vehicle:
    def __init__(self, x, y, max_width, max_height):
        self.location = PVector(x,y)
        width = 20
        height = 25
        self.max_width = max_width
        self.max_height = max_height
        self.rect = Rect(x - width/2, y - height/2, width, height)
        self.color = (0, 200, 0)
        
        self.surf = Surface((self.rect.width, self.rect.height), flags=SRCALPHA)
        pygame.draw.polygon(self.surf, (0,0,0), [(width//2,0), (0,height), (width,height)], 0)
        self.original_surf = self.surf.copy()

        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)

        self.r = 10.0
        self.max_speed = 4
        self.max_force = 0.1

        self.angle = 0

        self.target = PVector(0,0)

        self.brain = Perceptron(3)

    def update(self):
        self.velocity + self.acceleration
        self.velocity.limit(self.max_speed)
        self.location + self.velocity
        self.acceleration * 0

        prev_angle = self.angle % 360
        to_target = PVector.sub(self.target, self.location).normalize()
        #screen.draw.line((0,0,0), (self.location.x, self.location.y), (self.target.x, self.target.y))

        pa = math.radians(prev_angle)
        angle_x = self.location.x + math.cos(pa) * 100
        angle_y = self.location.y + math.sin(pa) * 100
        #screen.draw.line((255,0,0), (self.location.x, self.location.y), (angle_x, angle_y))

        target_angle = to_target.heading()
        if target_angle < 0:
            target_angle += 360

        delta = (target_angle - prev_angle)
        if delta > 180:
            delta = -(360 - delta)
        if delta < -180:
            delta = 360 + delta

        adjust = 0
        if delta > 1:
            adjust = 3
        elif delta < -1:
            adjust = -3

        self.angle = prev_angle + adjust
        self.rotate()

    def draw(self):
        screen.blit(self.surf, (self.rect.x, self.rect.y))

    def apply_force(self, force):
        self.acceleration + force

    def wander(self):
        projected_distance = 100
        angle_x = self.location.x + math.cos(math.radians(self.angle)) * projected_distance
        angle_y = self.location.y + math.sin(math.radians(self.angle)) * projected_distance
        #screen.draw.circle(angle_x, angle_y, 10, (0,255,0))
        predicted = PVector(angle_x, angle_y)

        r = 50
        #screen.draw.circle(angle_x, angle_y, r, (0,0,0), 1)
        random_angle = uniform(0,360)
        target_x = angle_x + math.cos(math.radians(random_angle)) * r
        target_y = angle_y + math.sin(math.radians(random_angle)) * r
        #screen.draw.circle(target_x, target_y, 5, (0,255,0))

        boundary = 25
        if target_x > self.max_width - boundary:
            target_x = self.max_width//2
        if target_x < boundary:
            target_x = self.max_width//2
        if target_y > self.max_height - boundary:
            target_y = self.max_height//2
        if target_y < boundary:
            target_y = self.max_height//2

        self.seek(PVector(target_x, target_y))

    def seek(self, target):
        self.target = target
        d = PVector.sub(target, self.location)
        distance = d.mag()
        desired = PVector.normalize(d)

        if distance < 100:
            m = remap(distance, 0, 100, 0, self.max_speed)
            desired * m
        else:
            desired * self.max_speed

        steer = PVector.sub(desired, self.velocity)
        steer.limit(self.max_force)
        return steer

    def seek_targets(self, targets):
        forces = []
        for i in range(len(targets)):
            forces.append(self.seek(targets[i]))

        output = self.brain.process(forces)
        self.apply_force(output)

        desired = PVector(WIDTH//2, HEIGHT//2)
        error = PVector.sub(desired, self.location)
        self.brain.train_vehicle(forces, error)

    def rotate(self):
        self.surf = transform.rotate(self.original_surf, -self.angle - 90)
        w,h = self.surf.get_size()
        self.rect = Rect(self.location.x-w/2, self.location.y-h/2, w, h)

    def follow(self, field):
        int_location = PVector(int(self.location.x), int(self.location.y))
        desired = field.lookup(int_location)
        desired * self.max_speed
        steer = PVector.sub(desired, self.velocity)
        steer.limit(self.max_force)
        self.apply_force(steer)

    def track(self, path):
        predict = self.velocity.normalize()
        predict * 25
        predict_loc = PVector.add(self.location, predict)

        screen.draw.circle(predict_loc.x, predict_loc.y, 25, (255,0,0))

        record = 1000000
        normal_point = None
        for i in range(len(path.points)-1):
            a = PVector(*path.points[i])
            b = PVector(*path.points[i+1])

            np = Vehicle.get_normal_point(predict_loc, a, b)

            if (np.x < min(a.x, b.x) or np.x > max(a.x, b.x)):
                np = b.copy()

            d = PVector.dist(predict_loc, np)
            if d < record:
                record = d
                normal_point = np.copy()

        screen.draw.circle(normal_point.x, normal_point.y, 15, (0,0,255))

        distance = PVector.dist(predict_loc, normal_point)
        if distance > path.radius:
            self.seek(normal_point) # this one will turn back

    def get_normal_point(p, a, b):
        ap = PVector.sub(p, a)
        ab = PVector.sub(b, a)

        ab = ab.normalize()
        ab * ap.dot(ab)

        normal_point = PVector.add(a, ab)
        return normal_point

    def accelerate(self, amount):
        a = math.radians(self.angle)
        angle_x = self.location.x - math.cos(a) * amount
        angle_y = self.location.y - math.sin(a) * amount
        force = PVector.sub(self.location, PVector(angle_x,angle_y))
        self.apply_force(force)

    def separate(self, others):
        desired_separation = self.r * 2
        total_force = PVector(0,0)
        count = 0

        for o in others:
            d = PVector.dist(self.location, o.location)
            if d > 0 and d < desired_separation:
                diff = PVector.sub(self.location, o.location)
                diff = diff.normalize()
                diff / d
                total_force + diff
                count += 1

        if count > 0:
            total_force / count
            total_force.set_mag(self.max_speed)
            steer = PVector.sub(total_force, self.velocity)
            steer.limit(self.max_force)
            return steer
        else:
            return PVector(0,0)

    def apply_behaviors(self, others):
        separate = self.separate(others)
        seek = self.seek(PVector(*pygame.mouse.get_pos()))

        separate * 1.5
        seek * 0.5

        self.apply_force(separate)
        self.apply_force(seek)

class Perceptron:
    c = 0.01

    def __init__(self, n):
        self.weights = [uniform(-1,1) for i in range(n)]

    def feedforward(self, inputs):
        sum_ = 0
        for i in range(len(self.weights)):
            sum_ += inputs[i] * self.weights[i]
        return self.activate(sum_)

    def activate(self, n):
        return 1 if n > 0 else -1

    def train(self, inputs, desired):
        guess = self.feedforward(inputs)
        error = desired - guess
        for i in range(len(self.weights)):
            self.weights[i] += Perceptron.c * error * inputs[i]

    def process(self, forces):
        sum_ = PVector(0,0)
        for i in range(len(self.weights)):
            forces[i] * self.weights[i]
            sum_ + forces[i]
        return sum_

    def train_vehicle(self, forces, error):
        for i in range(len(self.weights)):
            self.weights[i] + Perceptron.c * error.x * forces[i].x
            self.weights[i] + Perceptron.c * error.y * forces[i].y

class Trainer:
    def __init__(self, x, y, a):
        self.inputs = [x, y, 1]
        self.answer = a

def f(x):
    return x / 2 + 100

class Simulation:
    def __init__(self):
        self.p = Perceptron(3)
        self.training = []
        self.count = 0

        for i in range(2000):
            x = randint(0, WIDTH)
            y = randint(0, HEIGHT)
            if y < f(x):
                a = -1
            else:
                a = 1
            self.training.append(Trainer(x,y,a))

    def update(self):
        self.p.train(self.training[self.count].inputs, self.training[self.count].answer)
        self.count = (self.count + 1) % len(self.training)

    def draw(self):
        p1 = (0, f(0))
        p2 = (WIDTH, f(WIDTH))
        screen.draw.line((0,0,0), p1, p2)

        for i in range(self.count):
            guess = self.p.feedforward(self.training[i].inputs)
            if guess > 0:
                color = (0,0,255)
            else:
                color = (255,0,0)

            screen.draw.circle(self.training[i].inputs[0], self.training[i].inputs[1], 4, color, 0)

# ----------------------------------------------------
def update():
    v.seek_targets(targets)
    v.update()
# ----------------------------------------------------

# ----------------------------------------------------
def draw():
    v.draw()

    for i,t in enumerate(targets):
        screen.draw.circle(t.x, t.y, 8, (0,255,0), 0)
        screen.draw.circle(t.x, t.y, 8, (0,0,0), 1)
        screen.draw.text(str(i), pos=(t.x+8, t.y+8))

# ----------------------------------------------------

# ----------------------------------------------------
def setup():
    pass
# ----------------------------------------------------

# ----------------------------------------------------
v = Vehicle(WIDTH//2, HEIGHT//2, WIDTH, HEIGHT)

targets = [PVector(randint(0,WIDTH), randint(0,HEIGHT)) for i in range(5)]

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
