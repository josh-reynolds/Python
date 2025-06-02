from engine import *
from pvector import PVector

class FlowField:
    def __init__(self, resolution, max_width, max_height):
        self.resolution = resolution
        self.max_width = max_width
        self.max_height = max_height
        self.cols = max_width//resolution
        self.rows = max_height//resolution
        self.field = [[self.make_vector(i,j) for i in range(self.cols)] for j in range(self.rows)]

    def make_vector(self, col, row):
        center = (self.resolution * col + self.resolution//2, 
                  self.resolution * row + self.resolution//2)
        v = PVector.sub(PVector(self.max_width//2, self.max_height//2), PVector(*center))
        return PVector.normalize(v)

    def draw(self):
        for x in range(self.cols):
            for y in range(self.rows):
                self.draw_cell(y,x)

    def draw_cell(self, x, y):
        top = self.resolution * y
        left = self.resolution * x
        width = self.resolution
        height = self.resolution

        fill = 1

        center = (top + self.resolution//2, left + self.resolution//2)
        end = (center[0] + self.field[x][y].x * 20, center[1] + self.field[x][y].y * 20)

        screen.draw.rect((top, left, width, height), (255,64,64), fill)
        screen.draw.circle(center[0], center[1], 3, (0,0,0))
        screen.draw.line((0,0,0), center, end)

    def lookup(self, vector):
        column = max(min(vector.x//self.resolution, self.cols), 0)
        row = max(min(vector.y//self.resolution, self.rows), 0)
        return self.field[row][column]
