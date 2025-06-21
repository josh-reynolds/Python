import math
from random import uniform, randint
import pygame
from pygame import Rect, Surface, transform
from pygame.locals import SRCALPHA
from engine import remap, screen
from pvector import PVector

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

        self.brain = Perceptron(5)

    def update(self):
        self.velocity + self.acceleration
        self.velocity.limit(self.max_speed)
        self.location + self.velocity
        self.acceleration * 0

        prev_angle = self.angle % 360
        to_target = PVector.sub(self.target, self.location).normalize()

        pa = math.radians(prev_angle)
        angle_x = self.location.x + math.cos(pa) * 100
        angle_y = self.location.y + math.sin(pa) * 100

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

        desired = PVector(self.max_width//2, self.max_height//2)
        error = PVector.sub(desired, self.location)
        self.brain.train_vehicle(forces, error)

    def rotate(self):
        self.surf = transform.rotate(self.original_surf, -self.angle - 90)
        w,h = self.surf.get_size()
        self.rect = Rect(self.location.x-w/2, self.location.y-h/2, w, h)

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
    def __init__(self, max_width, max_height):
        self.max_width = max_width
        self.max_height = max_height
        self.p = Perceptron(3)
        self.training = []
        self.count = 0

        for i in range(2000):
            x = randint(0, max_width)
            y = randint(0, max_height)
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
        p2 = (self.max_width, f(self.max_width))
        screen.draw.line((0,0,0), p1, p2)

        for i in range(self.count):
            guess = self.p.feedforward(self.training[i].inputs)
            if guess > 0:
                color = (0,0,255)
            else:
                color = (255,0,0)

            screen.draw.circle(self.training[i].inputs[0], self.training[i].inputs[1], 4, color, 0)

class VehicleSimulation:
    def __init__(self, max_width, max_height):
        self.v = Vehicle(max_width//2, max_height//2, max_width, max_height)
        self.targets = [PVector(randint(0,max_width), randint(0,max_height)) for i in range(5)]

    def update(self):
        self.v.seek_targets(self.targets)
        self.v.update()

    def draw(self):
        self.v.draw()

        for i,t in enumerate(self.targets):
            screen.draw.circle(t.x, t.y, 8, (0,255,0), 0)
            screen.draw.circle(t.x, t.y, 8, (0,0,0), 1)
            screen.draw.text(str(i), pos=(t.x+8, t.y+8))
