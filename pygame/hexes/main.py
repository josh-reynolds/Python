import math
import os.path
import pygame
from engine import *

WIDTH = 425
HEIGHT = 550
TITLE = "Hexes"

class Hex:
    def __init__(self, screen_coordinate, radius, color, width):
        self.x, self.y = screen_coordinate
        self.radius = radius
        self.color = color
        self.width = width

    def draw(self):
        screen.draw.hex(self.x, self.y, self.radius, self.color, self.width)

class SubdividedHex(Hex):
    def __init__(self, screen_coordinate, radius, color, width, scale):
        super().__init__(screen_coordinate, radius, color, width)
        self.scale = scale
        self.subhexes = Rosette((self.x, self.y), scale-2, radius/scale, (0,0,0))

    def draw(self):
        screen.draw.hex(self.x, self.y, self.radius, self.color, self.width)
        self.subhexes.draw()

class Grid:
    def __init__(self, hex_radius, top_border, left_border, columns, rows, color, width=1):
        self.hex_radius = hex_radius
        self.y_offset = math.sqrt((hex_radius * hex_radius) - (hex_radius/2 * hex_radius/2))

        self.start_x = hex_radius + left_border
        self.start_y = int(self.y_offset) + top_border

        self.top_border = top_border
        self.left_border = left_border
        self.columns = columns
        self.rows = rows

        self.hexes = []
        for i in range(columns):
            for j in range(rows):
                self.add_hex(i, j, color, width)

    def add_hex(self, i, j, color, width):
        self.hexes.append(Hex(self.hex_coordinate_to_screen(i,j), self.hex_radius, color, width))

    def hex_coordinate_to_screen(self, column, row):
        x = self.start_x + column * self.hex_radius * 1.5
        columnAdjust = 0 if column % 2 == 0 else self.y_offset
        y = self.start_y + self.y_offset * row * 2 + columnAdjust
        return (x,y)

    def draw(self):
        for h in self.hexes:
            h.draw()

class SubdividedGrid(Grid):
    def __init__(self, hex_radius, top_border, left_border, columns, rows, color, width=1, scale=4):
        self.scale = scale
        super().__init__(hex_radius, top_border, left_border, columns, rows, color, width=1)

    def add_hex(self, i, j, color, width):
        self.hexes.append(SubdividedHex(self.hex_coordinate_to_screen(i,j), 
                                        self.hex_radius, color, width, self.scale))

class Rosette:
    def __init__(self, coordinate, radius, hex_radius, color, width=1):
        self.coordinate = coordinate
        self.radius = radius
        self.hex_radius = hex_radius
        self.y_offset = math.sqrt((hex_radius * hex_radius) - (hex_radius/2 * hex_radius/2))

        self.hexes = []
        self.hexes.append(Hex((coordinate[0], coordinate[1]), hex_radius, color, width))

        for i in range(radius):
            pass

        if radius > 0:
            for i in range(6):
                angle = math.pi * 2/6 * (i+1) + math.pi/6
                vx = 2 * self.y_offset * math.cos(angle) + coordinate[0]
                vy = 2 * self.y_offset * math.sin(angle) + coordinate[1]
                self.hexes.append(Hex((vx,vy), hex_radius, color, width))

        if radius > 1:
            for i in range(6):
                angle = math.pi * 2/6 * (i+1)
                vx = 3.5 * self.y_offset * math.cos(angle) + coordinate[0]
                vy = 3.5 * self.y_offset * math.sin(angle) + coordinate[1]
                self.hexes.append(Hex((vx,vy), hex_radius, color, width))

        if radius > 2:
            for i in range(6):
                angle = math.pi * 2/6 * (i+1) + math.pi/6
                vx = 4 * self.y_offset * math.cos(angle) + coordinate[0]
                vy = 4 * self.y_offset * math.sin(angle) + coordinate[1]
                self.hexes.append(Hex((vx,vy), hex_radius, color, width))

        if radius > 3:
            for i in range(6):
                angle1 = math.pi * 2/6 * (i+1) + math.pi/16.5
                vx1 = 5.3 * self.y_offset * math.cos(angle1) + coordinate[0]
                vy1 = 5.3 * self.y_offset * math.sin(angle1) + coordinate[1]
                self.hexes.append(Hex((vx1,vy1), hex_radius, color, width))

                angle2 = math.pi * 2/6 * (i+1) - math.pi/16.5
                vx2 = 5.3 * self.y_offset * math.cos(angle2) + coordinate[0]
                vy2 = 5.3 * self.y_offset * math.sin(angle2) + coordinate[1]
                self.hexes.append(Hex((vx2,vy2), hex_radius, color, width))

    def draw(self):
        for h in self.hexes:
            h.draw()

def update():
    pass

def draw():
    #g1.draw()
    #g2.draw()
    #g3.draw()
    #g4.draw()
    #g5.draw()
    #g6.draw()
    sg.draw()
    #r.draw()

    try:
        filename = "./output.png"
        if not os.path.isfile(filename):
            pygame.image.save(screen.surface, filename)
    except Exception as e:
        print(e)

g1 = Grid(10, 4, 8, 27, 31, (0,0,0))
g2 = Grid(20, 4, 12, 13, 15, (0,0,0), 2)    # 7 subhexes  (1 + 6)
g3 = Grid(30, 4, 16, 8, 10, (0,0,0), 2)     # 13 subhexes (1 + 6 + 6)
g4 = Grid(40, 12, 8, 6, 7, (0,0,0), 2)      # 19 subhexes (1 + 6 + 6 + 6)
g5 = Grid(50, 12, 12, 5, 5, (0,0,0), 2)     # 31 subhexes (1 + 6 + 6 + 6 + 12)
g6 = Grid(60, 12, 17, 4, 4, (0,0,0), 2)     # 43 subhexes (1 + 6 + 6 + 6 + 12 + 12)

sg = SubdividedGrid(40, 12, 8, 6, 7, (0,0,0), 2, 4)

r = Rosette((WIDTH/2, HEIGHT/2), 1, 40, (0,0,0))

run()

# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vx = radius * cos(angle)
#         vy = radius * sin(angle)
