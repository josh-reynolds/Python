from engine import *

class Grid:
    def __init__(self, resolution, max_width, max_height):
        self.resolution = resolution
        self.cols = max_width//resolution
        self.rows = max_height//resolution
        self.field = [[0 for i in range(self.cols)] for j in range(self.rows)]

    def draw(self, skip):
        for x in range(self.cols):
            for y in range(self.rows):
                self.draw_cell(y, x, skip)

    def draw_cell(self, x, y, skip):
        top = self.resolution * y
        left = self.resolution * x
        width = self.resolution
        height = self.resolution

        fill = (x + y) % skip
        screen.draw.rect((top, left, width, height), (255,64,64), fill)
