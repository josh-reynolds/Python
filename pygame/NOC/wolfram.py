import pygame
from pygame import Surface
from engine import *

class CA:
    def __init__(self, max_width, max_height):
        self.w = 1

        #self.ruleset = [0,1,0,1,1,0,1,0]   # Rule 90 - Sierpinski Triangle
        self.ruleset = [0,1,1,1,1,0,0,0]    # Rule 30 - Class 3 Random
        #self.ruleset = [0,1,1,1,0,1,1,0]    # Rule 110 - Class 3 Random

        self.cells = [[0 for i in range(max_width//self.w)] for j in range(max_height//self.w)]
        self.cells[0][len(self.cells[0])//2] = 1
        self.generate()

        self.image = Surface((max_width,max_height))
        for i in range(max_height//self.w):
            for j in range(len(self.cells[0])):
                if self.cells[i][j] == 1:
                    color = (0,0,0)
                else:
                    color = (255,255,255)
    
                pygame.draw.rect(self.image, color, (j*self.w, i*self.w, self.w, self.w), 0)

    def generate(self):
        #for i in range(HEIGHT//self.w-1):
        for i in range(len(self.cells)-1):
            nextrow = [0 for i in range(len(self.cells[0]))]
            for j in range(1, len(self.cells[0])-1):
                left = self.cells[i][j-1]
                me = self.cells[i][j]
                right = self.cells[i][j+1]

                nextrow[j] = self.rules(left, me, right)

            self.cells[i+1] = nextrow

    def rules(self, a, b, c):
        s = "" + str(a) + str(b) + str(c)
        index = int(s, 2)
        return self.ruleset[index]

    def draw(self):
        screen.blit(self.image, (0, 0))
