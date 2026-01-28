"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
from random import randint
from engine import screen, run
from pvector import PVector
from screen_matrix import push_matrix, pop_matrix, line, rotate, translate
from screen_matrix import equilateral_triangle

WIDTH = 1100
HEIGHT = 850
TITLE = "How to Host a Dungeon"

GROUND_LEVEL = HEIGHT // 5
STRATA_HEIGHT = (HEIGHT - GROUND_LEVEL) // 6
COLUMN_WIDTH = WIDTH // 12
BEAD = 30
FINGER = HEIGHT // 5

SKY = (36, 87, 192)
GROUND = (81, 76, 34)
MITHRIL = (255,255,255)
GOLD = (255, 0, 0)    # yes, this is red - text says 'draw a red line...'
BORDER = (0, 0, 0)
CAVERN = (0, 0, 0)
WATER = (0, 0, 255)

locations = []

def get_random_underground_location() -> PVector:
    return PVector(randint(0,WIDTH), randint(GROUND_LEVEL,HEIGHT))

def nearest_corner(point: PVector) -> PVector:
    if point.x < WIDTH/2:
        if point.y < HEIGHT/2:
            return PVector(0,0)
        return PVector(0,HEIGHT)
    if point.y < HEIGHT/2:
        return PVector(WIDTH,0)
    return PVector(WIDTH,HEIGHT)

class Mithril():
    def __init__(self):
        self.center = get_random_underground_location()
        self.radius = FINGER // 2
        self.corner = nearest_corner(self.center)

        corner_vector = PVector.normalize(PVector.sub(self.center, self.corner))
        self.angle = math.radians(corner_vector.heading()) + math.pi

    def update(self):
        pass

    def draw(self):
        push_matrix()
        translate(self.center.x, self.center.y)
        rotate(self.angle)
        equilateral_triangle(self.radius, MITHRIL, 0)
        equilateral_triangle(self.radius, BORDER, 2)
        pop_matrix()

        screen.draw.text("Mithril", center=(self.center.x, self.center.y))


class UndergroundRiver():
    def __init__(self):
        self.vertices = []

        self.caves = []
        self.lakes = []
        
        current_x = 0
        current_y = strata_depth(randint(0,5))

        while current_x < WIDTH and current_y < HEIGHT and current_y > GROUND_LEVEL:
            self.vertices.append(PVector(current_x, current_y))
            current_x += FINGER

            check = randint(0,9)
            match check:
                case 0 | 1 | 2:
                    pass
                case 3 | 4:
                    current_y += STRATA_HEIGHT
                case 5 | 6:
                    current_y -= STRATA_HEIGHT
                case 7 | 8:
                    self.caves.append(PVector(current_x, current_y))
                case 9:
                    current_x -= FINGER
                    current_y += STRATA_HEIGHT // 2

            if current_y < GROUND_LEVEL:
                x1, y1 = self.vertices[-1].x, self.vertices[-1].y
                x2, y2 = current_x, current_y
                slope = (y2 - y1) / (x2 - x1)
                intercept = y1 - (slope * x1)

                lake_y = GROUND_LEVEL
                lake_x = (lake_y - intercept) / slope

                self.lakes.append(PVector(lake_x,lake_y))

        self.vertices.append(PVector(current_x, current_y))

    def update(self):
        pass

    def draw(self):
        for c in self.caves:
            screen.draw.circle(c.x, c.y, BEAD, CAVERN, 0)

        for l in self.lakes:
            screen.draw.circle(l.x, l.y, BEAD, WATER, 0)
            
        for i,v in enumerate(self.vertices[:-1]):
            screen.draw.line(WATER, 
                             (v.x, v.y),
                             (self.vertices[i+1].x, self.vertices[i+1].y),
                             8)
        screen.draw.text("Underground River", pos=(self.vertices[0].x, self.vertices[0].y))

class GoldVein():
    def __init__(self):
        self.left = PVector(0, strata_depth(randint(0,5)))
        self.right = PVector(WIDTH, strata_depth(randint(0,5)))
        self.midpoint = PVector(WIDTH//2, 
                                (self.right.y - self.left.y)//2 + self.left.y)

    def update(self):
        pass

    def draw(self):
        screen.draw.line(GOLD, 
                         (self.left.x, self.left.y),
                         (self.right.x, self.right.y),
                         8)
        screen.draw.text("Gold Vein", center=(self.midpoint.x, self.midpoint.y))


class NaturalCavern():
    def __init__(self):
        self.center = get_random_underground_location()
        self.radius = BEAD
        self.tunnel = False
        self.tilt = 0
        self.contents = None

        detail = randint(1,6)
        match detail:
            case 1:
                self.tunnel = True
                self.tilt = randint(-FINGER//2, FINGER//2)
            case 2:
                self.contents = f"Plague {randint(1,4)}"
            case 3:
                self.contents = f"Gemstones {randint(1,4)}"
            case 4:
                pass
            case 5:
                self.contents = f"Primordial Beasts 1"
            case 6:
                self.contents = f"Fate 1"

    def update(self):
        pass

    def draw(self):
        screen.draw.circle(self.center.x, self.center.y, self.radius, CAVERN, 0)

        if self.tunnel:
            screen.draw.line(CAVERN,
                             (self.center.x - FINGER//2, self.center.y - self.tilt),
                             (self.center.x + FINGER//2, self.center.y + self.tilt),
                             12)

        if self.contents:
            y_offset = -10
        else:
            y_offset = 0

        screen.draw.text("Cavern", 
                         center=(self.center.x, self.center.y + y_offset),
                         color = (255,255,255))

        if self.contents:
            screen.draw.text(self.contents, 
                             center=(self.center.x, self.center.y - y_offset),
                             color = (255,255,255))


class CaveComplex():
    def __init__(self):
        self.radius = BEAD
        self.center_1 = get_random_underground_location()

    def update(self):
        pass

    def draw(self):
        screen.draw.circle(self.center_1.x, self.center_1.y, self.radius, CAVERN, 0)

        screen.draw.text("Cavern", 
                         center=(self.center_1.x, self.center_1.y - 10),
                         color = (255,255,255))

        screen.draw.text("Primordial Beasts 1", 
                         center=(self.center_1.x, self.center_1.y + 10),
                         color = (255,255,255))


def strata_depth(strata: int) -> int:
    return GROUND_LEVEL + STRATA_HEIGHT * strata + STRATA_HEIGHT//2

def update():
    for location in locations:
        location.update()

def draw():
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)

    for location in locations:
        location.draw()

    for i in range(6):
        screen.draw.text(f"{i+1}", center=(10, strata_depth(i)))
        screen.draw.text(f"{i+1}", center=(WIDTH-10, strata_depth(i)))

    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

    #print(screen.surface.get_at((WIDTH//2,HEIGHT//2)))

def add_caverns():
    locations.append(NaturalCavern())
    cavern_count = 1
    while randint(1,6) < 6 and cavern_count < 6:
        locations.append(NaturalCavern())
        cavern_count += 1

# Primordial Age events
locations.append(Mithril())
locations.append(Mithril())
locations.append(GoldVein())
add_caverns()
locations.append(UndergroundRiver())
locations.append(CaveComplex())

run()
