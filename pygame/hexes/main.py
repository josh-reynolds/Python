"""Draw a grid of hexagons at various scales."""
import math
import os.path
import pygame
from engine import screen, run

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

class NumberedHex(Hex):
    def __init__(self, screen_coordinate, radius, color, width, text):
        super().__init__(screen_coordinate, radius, color, width)
        self.text = text

    def draw(self):
        super().draw()
        screen.draw.fontsize = 24    # TO_DO: awkward API, fix this!
        screen.draw.fontcolor = (128,128,128)
        screen.draw.set_font()
        screen.draw.text(self.text, center=(self.x, self.y+self.radius-18))
        # hard-coded positioning values, should fix this too
        # (same applies to font size - should scale w/ radius)

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

class NumberedGrid(Grid):
    def add_hex(self, i, j, color, width):
        text = f"{i:02d}{j:02d}"
        self.hexes.append(NumberedHex(self.hex_coordinate_to_screen(i,j), 
                                      self.hex_radius, color, width, text))

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

        # still seeing artifacts here. we've corrected the underlying hexes, now need
        # to fix the layout here...
        # hardcoding and guesstimate values below were never great to begin with,
        # always hoped to get something formulaic that could drive through the
        # (currently idle) loop below

        # 1) adjust for floating point issues here, just as with hex vertices
        # 2) fold in proper math for layout of hex centers

        # for a flat-topped hex:
        # hex vertices are 60 degrees apart, starting at 60 degrees
        # neighboring hex centers are also 60 degrees apart, but starting at 30 degrees
        # the first ring has 6 hexes, the second 12, the third 18, the fourth 24:
        #  6 vertex hexes + ((ring # - 1) * 6)
        #    1 = 6 + 0 * 6 = 6
        #    2 = 6 + 1 * 6 = 12
        #    3 = 6 + 2 * 6 = 18
        #    4 = 6 + 3 * 6 = 24
        #    5 = 6 + 4 * 6 = 30
        #    6 = 6 + 5 * 6 = 36
        
        # the angular distance from vertex hex to vertex hex is 60 degrees, so
        # side hexes just divvy up that separation (add one for fencepost)
        #   1 = 0 side hexes = 0 separation:              30 | 90
        #   2 = 1 side hex   = 60 / (1 + 1) = 30 degrees: 30 | 60 | 90
        #   3 = 2 side hexes = 60 / (2 + 1) = 20 degrees: 30 | 50 | 70 | 90
        #   4 = 3 side hexes = 60 / (3 + 1) = 15 degrees: 30 | 45 | 60 | 75 | 90
        #   5 = 4 side hexes = 60 / (4 + 1) = 12 degrees: 30 | 42 | 54 | 66 | 78 | 90
        #   6 = 5 side hexes = 60 / (5 + 1) = 10 degrees: 30 | 40 | 50 | 60 | 70 | 80 | 90

        # nice how hexes produce integer values up to this point, but at a ring size of 7
        # we'll start to see floating point values and all the potential issues there - we
        # might want to limit rosettes to that max size

        # per the floating point math comments above, it might also be useful to 
        # keep a couple tables of trig values so we have consistency (and theoretically speed,
        # though that's not really a concern here)

        # When fixing the hex vertices, I discovered that in Python, math.sin(180) and math.sin(360), 
        # for instance, are not quite 0 as they should be, and this tiny value was at least one
        # of the issues contributing to visual artifacts. So same applies here.

        # these tables need to go all the way around to 360...
        # not sure it's worth the effort, since in testing, Python math.sin()/cos()
        # give these same values when rounded to 5 decimal places
        # ...and if I do round(math.sin(math.radians(180)),5) I also get 0, so is that enough?
        sins = {30:0.5, 40:0.64279, 42:0.66913, 45:0.70711, 
                50:0.76604, 54:0.80902, 60:0.86603, 66:0.91355, 
                70:0.93969, 75:0.96593, 78:0.97815,
                80:0.98481, 90:1.0}

        coss = {30:0.86603, 40:0.76604, 42:0.74314, 45:0.70711, 
                50:0.64279, 54:0.58779, 60:0.5, 66:0.40674, 
                70:0.34202, 75:0.25882, 78:0.20791,
                80:0.17365, 90:0}

        for i in range(radius):
            vertex_hex_count = 1
            edge_hex_count = i-1
            ring_hexes = 6 * (vertex_hex_count + edge_hex_count)

            pass

        if radius > 0:
            for i in range(6):
                # 60 degrees + 30 degrees
                angle = math.radians(60 * (i+1) + 30)
                vx = 2 * self.y_offset * math.cos(angle) + coordinate[0]
                vy = 2 * self.y_offset * math.sin(angle) + coordinate[1]
                self.hexes.append(Hex((vx,vy), hex_radius, color, width))

        if radius > 1:
            for i in range(6):
                # 60 degrees
                angle = math.radians(60 * (i+1))
                vx = 3.5 * self.y_offset * math.cos(angle) + coordinate[0]
                vy = 3.5 * self.y_offset * math.sin(angle) + coordinate[1]
                self.hexes.append(Hex((vx,vy), hex_radius, color, width))

        if radius > 2:
            for i in range(6):
                # 60 degrees + 30 degrees
                angle = math.radians(60 * (i+1) + 30)
                vx = 4 * self.y_offset * math.cos(angle) + coordinate[0]
                vy = 4 * self.y_offset * math.sin(angle) + coordinate[1]
                self.hexes.append(Hex((vx,vy), hex_radius, color, width))

        if radius > 3:
            for i in range(6):
                # 60 degrees + 11 degrees
                angle1 = math.pi * 2/6 * (i+1) + math.pi/16.5
                vx1 = 5.3 * self.y_offset * math.cos(angle1) + coordinate[0]
                vy1 = 5.3 * self.y_offset * math.sin(angle1) + coordinate[1]
                self.hexes.append(Hex((vx1,vy1), hex_radius, color, width))

                # 60 degrees - 11 degrees
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
    #sg.draw()
    #r.draw()
    #h.draw()
    #g11.draw()
    #g41.draw()
    #g51.draw()
    #g61.draw()
    #num_hex.draw()
    ng1.draw()

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

r = Rosette((WIDTH//2, HEIGHT//2), radius=2, hex_radius=40, color=(0,0,0))

h = Hex((WIDTH//2, HEIGHT//2), 80, (0,0,0), 1)

for i in range(7):
    if i > 0:
        vertex_hex_count = 1
        edge_hex_count = i-1
        ring_hexes = 6 * (vertex_hex_count + edge_hex_count)
        #print(i, vertex_hex_count, edge_hex_count, ring_hexes)

# aligning first hex center with screen origin, and filling entire page
g11 = Grid(10, -10, -10, 33, 33, (0,0,0))
g41 = Grid(40, -37, -40, 8, 9, (0,0,0), 2)     # 19 subhexes (1 + 6 + 6 + 6)
g51 = Grid(50, -46, -50, 7, 8, (0,0,0), 2)     # 31 subhexes (1 + 6 + 6 + 6 + 12)
g61 = Grid(60, -54, -60, 5, 6, (0,0,0), 2)     # 43 subhexes (1 + 6 + 6 + 6 + 12 + 12)

num_hex = NumberedHex((WIDTH/2, HEIGHT/2), 60, (0,0,0), 1, "0101")
ng1 = NumberedGrid(50, -46, -50, 7, 8, (0,0,0), 2)

run()

# vertices in a regular polygon:
#     for i in sides:
#         angle = TWO_PI/sides * i
#         vx = radius * cos(angle)
#         vy = radius * sin(angle)
