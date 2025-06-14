import pygame
from pygame.locals import *
from engine import *
from screen_matrix import sm, line, translate, rotate, push_matrix, pop_matrix

class Rule:
    def __init__(self, p, s):
        self.predecessor = p
        self.successor = s

class LSystem:
    def __init__(self, axiom, ruleset):
        self.axiom = axiom
        self.ruleset = ruleset

    def generate(self):
        next_ = []

        for i in range(len(self.axiom)):
            c = self.axiom[i]
            for j in self.ruleset:
                if c == j.predecessor:
                    next_.append(j.successor)
                else:
                    next_.append(c)

        self.axiom = ''.join(next_)

    def get_sentence(self):
        return self.axiom

class Turtle:
    def __init__(self, sentence, length, angle):
        self.length = length
        self.angle = angle
        self.set_to_do(sentence)

    def change_len(self, factor):
        self.length *= factor

    def render(self):
        screen.fill(Color("white"))
        for i in self.to_do:
            exec(i)
        pygame.display.update()

    def set_to_do(self, sentence):
        self.to_do = []
        for c in sentence:
            if c == 'F':
                self.to_do.append(f"line(0,0,{self.length},0)")
                self.to_do.append(f"translate({self.length},0)")
            elif c == 'G':
                self.to_do.append(f"translate({self.length},0)")
            elif c == '+':
                self.to_do.append(f"rotate({self.angle})")
            elif c == '-':
                self.to_do.append(f"rotate(-{self.angle})")
            elif c == '[':
                self.to_do.append(f"push_matrix()")
            elif c == ']':
                self.to_do.append(f"pop_matrix()")
