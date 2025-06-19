from random import randint, random, choice
import pygame
from pygame import Rect
from engine import *

class Faces:
    def __init__(self):
        mutation_rate = 0.05
        self.population = Population(mutation_rate, 5)
        self.button = Button(15, 175, 180, 20, "evolve new generation")

    def update(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        self.population.rollover(mouseX, mouseY)
        if self.button.clicked(mouseX, mouseY):
            self.population.selection()
            self.population.reproduction()

    def draw(self):
        self.population.draw()
        self.button.draw()

class DNA:
    def __init__(self):
        self.genes = [random() for i in range(10)]

    def __repr__(self):
        result = [f"{self.genes[i]:0.2f}" for i in range(len(self.genes))]
        return str(result)

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
                self.genes[i] = random()

class Face:
    def __init__(self, left, top):
        self.dna = DNA()
        self.fitness = 0
        self.border_color = (0,0,0)
        self.reset_location(left, top)

    def reset_location(self, left, top):
        self.rect = Rect(left, top, 160, 160)
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

    def draw(self):
        radius = remap(self.dna.genes[0], 0, 1, 20, 70)
        color = (int(self.dna.genes[1] * 255), 
                 int(self.dna.genes[2] * 255), 
                 int(self.dna.genes[3] * 255))
        screen.draw.circle(self.x, self.y, radius, color)

        eye_y = remap(self.dna.genes[4], 0, 1, 0, 15)
        eye_x = remap(self.dna.genes[5], 0, 1, 0, radius)
        eye_size = remap(self.dna.genes[5], 0, 1, 3, 15)
        eye_color = (int(self.dna.genes[4] * 255), 
                     int(self.dna.genes[5] * 255), 
                     int(self.dna.genes[6] * 255))
        screen.draw.circle(self.x - eye_x, self.y - eye_y, eye_size, eye_color)
        screen.draw.circle(self.x + eye_x, self.y - eye_y, eye_size, eye_color)

        mouth_color = (int(self.dna.genes[7] * 255), 
                       int(self.dna.genes[8] * 255), 
                       int(self.dna.genes[9] * 255))
        mouth_x = remap(self.dna.genes[5], 0, 1, -25, 25)
        mouth_y = remap(self.dna.genes[5], 0, 1, 0, 25)
        mouthw = remap(self.dna.genes[5], 0, 1, 0, 50)
        mouthh = remap(self.dna.genes[5], 0, 1, 0, 10)
        screen.draw.rect((self.x + mouth_x, self.y + mouth_y, mouthw, mouthh), mouth_color, 0)

        screen.draw.rect(self.rect, self.border_color, 1)

        screen.draw.text(str(self.fitness), (self.rect.left + 10, self.rect.top + 10))  

    def rollover(self, mouseX, mouseY):
        if self.rect.collidepoint((mouseX, mouseY)):
            self.border_color = (255,0,0)
            self.fitness += 1
        else:
            self.border_color = (0,0,0)

    def crossover(self, partner):
        child = Face(self.rect.left, self.rect.top)
        child.dna = self.dna.crossover(partner.dna)
        return child

    def mutate(self, mutation_rate):
        self.dna.mutate(mutation_rate)

class Population:
    def __init__(self, mutation_rate, size):
        self.mutation_rate = mutation_rate
        self.size = size
        self.faces = [Face((10 * i + 10) + 160 * i, 10) for i in range(self.size)]

    def rollover(self, mouseX, mouseY):
        for f in self.faces:
            f.rollover(mouseX, mouseY)

    def draw(self):
        for f in self.faces:
            f.draw()

    def selection(self):
        print("Population.selection()")
        self.mating_pool = []
        for p in self.faces:
            n = int(p.fitness)
            for i in range(n):
                self.mating_pool.append(p)

        if len(self.mating_pool) == 0:
            for i in range(len(self.faces)):
                self.mating_pool.append(self.faces[i])
            print("zero pool")

        total_fitness = 0
        for r in self.mating_pool:
            total_fitness += r.fitness
        print(f"Average mating pool fitness: {total_fitness/len(self.mating_pool):0.5f}")

    def reproduction(self):
        print("Population.reproduction()")
        for i in range(len(self.faces)):
            parent_a = choice(self.mating_pool)
            parent_b = choice(self.mating_pool)

            child = parent_a.crossover(parent_b)
            child.reset_location((10 * i + 10) + 160 * i, 10)
            child.mutate(self.mutation_rate)

            self.faces[i] = child

class Button:
    def __init__(self, x, y, w, h, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.rect = Rect(x, y, w, h)
        self.active = False

    def clicked(self, mouseX, mouseY):
        if ((pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[1]) and
            self.rect.collidepoint((mouseX, mouseY)) and not self.active):
            self.color = (255,128,128)
            self.active = True
            return True
        else:
            if (not pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[1]):
                self.active = False
            self.color = (255,255,255)
            return False

    def draw(self):
        screen.draw.rect(self.rect, self.color, 0)
        screen.draw.rect(self.rect, (0,0,0))
        screen.draw.text(self.text, pos=(self.x + 2, self.y))
