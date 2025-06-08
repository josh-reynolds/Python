from random import randint
from engine import *

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.previous = randint(0,1)
        self.state = self.previous

class Life:
    def __init__(self, max_width, max_height):
        self.w = 10
        self.columns = max_width//self.w
        self.rows = max_height//self.w
        
        self.board = [[Cell(x,y) for x in range(self.columns)] for y in range(self.rows)]

    def generate(self):
        for x in range(1,self.columns-1):
            for y in range(1,self.rows-1):
                self.board[y][x].previous = self.board[y][x].state

        for x in range(1,self.columns-1):
            for y in range(1,self.rows-1):
                neighbors = 0
                for i in range(-1,2):
                    for j in range(-1,2):
                        neighbors += self.board[y+i][x+j].previous
                neighbors -= self.board[y][x].previous

                if self.board[y][x].previous == 1 and neighbors < 2:
                    self.board[y][x].state = 0
                elif self.board[y][x].previous == 1 and neighbors > 3:
                    self.board[y][x].state = 0
                elif self.board[y][x].previous == 0 and neighbors == 3:
                    self.board[y][x].state = 1
                else:
                    self.board[y][x].state = self.board[y][x].previous

    def draw(self):
        for x in range(self.columns):
            for y in range(self.rows):
                cell = self.board[y][x]

                if cell.state == 1 and cell.previous == 0:
                    color = (0,0,255)
                elif cell.state == 1 and cell.previous == 1:
                    color = (0,0,0)
                elif cell.state == 0 and cell.previous == 1:
                    color = (255,0,0)
                elif cell.state == 0 and cell.previous == 0:
                    color = (255,255,255)

                screen.draw.rect((x*self.w, y*self.w, self.w, self.w), color, 0)
                screen.draw.rect((x*self.w, y*self.w, self.w, self.w), (200,200,200), 1)
