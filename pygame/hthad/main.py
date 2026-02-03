"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
from random import randint, choice
from typing import List, Tuple
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
DWARF = (100, 80, 255)

show_labels = True

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
    def __init__(self) -> None:
        self.center = get_random_underground_location()
        self.radius = FINGER // 2
        self.corner = nearest_corner(self.center)

        corner_vector = PVector.normalize(PVector.sub(self.center, self.corner))
        self.angle = math.radians(corner_vector.heading()) + math.pi

        self.z_order = 0

    def update(self) -> None:
        pass

    def draw(self) -> None:
        push_matrix()
        translate(self.center.x, self.center.y)
        rotate(self.angle)
        equilateral_triangle(self.radius, MITHRIL, 0)
        equilateral_triangle(self.radius, BORDER, 2)
        pop_matrix()

        if show_labels:
            screen.draw.text("Mithril", center=(self.center.x, self.center.y))


class UndergroundRiver():
    def __init__(self) -> None:
        self.vertices = []

        self.caves = []
        self.lakes = []

        self.z_order = 0
        
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
                    self.caves.append(Cavern(PVector(current_x, current_y), None, False, 0))
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

    def update(self) -> None:
        pass

    def draw(self) -> None:
        for c in self.caves:
            c.draw()

        for l in self.lakes:
            screen.draw.circle(l.x, l.y, BEAD, WATER, 0)
            
        for i,v in enumerate(self.vertices[:-1]):
            screen.draw.line(WATER, 
                             (v.x, v.y),
                             (self.vertices[i+1].x, self.vertices[i+1].y),
                             8)
        if show_labels:
            screen.draw.text("Underground River", pos=(self.vertices[0].x, self.vertices[0].y))

class GoldVein():
    def __init__(self) -> None:
        self.left = PVector(0, strata_depth(randint(0,5)))
        self.right = PVector(WIDTH, strata_depth(randint(0,5)))
        self.midpoint = PVector(WIDTH//2, 
                                (self.right.y - self.left.y)//2 + self.left.y)
        self.z_order = 0

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.draw.line(GOLD, 
                         (self.left.x, self.left.y),
                         (self.right.x, self.right.y),
                         8)
        if show_labels:
            screen.draw.text("Gold Vein", center=(self.midpoint.x, self.midpoint.y))


class Location():
    def __init__(self, coordinate: PVector) -> None:
        self.coordinate = coordinate


class Entity():
    def __init__(self, name: str, parent: Location, color: Tuple) -> None:
        self.name = name
        self.parent = parent
        self.x = self.parent.coordinate.x
        self.y = self.parent.coordinate.y
        self.radius = BEAD//3
        self.color = color

    def __str__(self) -> str:
        return self.name

    def draw(self) -> None:
        screen.draw.circle(self.x, self.y, self.radius, self.color, 0)


class Cavern(Location):
    def __init__(self, coordinate: PVector, contents: Entity=None, 
                 tunnel: bool=False, tilt: int=0) -> None:
        super().__init__(coordinate)
        self.radius = BEAD//2
        self.tunnel = tunnel
        self.tilt = tilt
        self.contents = contents
        self.z_order = 2

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.draw.circle(self.coordinate.x, self.coordinate.y, self.radius, CAVERN, 0)

        if self.tunnel:
            screen.draw.line(CAVERN,
                             (self.coordinate.x - FINGER//2, self.coordinate.y - self.tilt),
                             (self.coordinate.x + FINGER//2, self.coordinate.y + self.tilt),
                             12)

        if self.contents:
            y_offset = -10
        else:
            y_offset = 0

        if show_labels:
            screen.draw.text("Cavern", 
                             center=(self.coordinate.x, self.coordinate.y + y_offset),
                             color = (255,255,255))

        if self.contents and show_labels:
            screen.draw.text(f"{self.contents}", 
                             center=(self.coordinate.x, self.coordinate.y - y_offset),
                             color = (255,255,255))

        if self.contents:
            self.contents.draw()

class Room(Location):
    def __init__(self, coordinate: PVector, contents: Entity=None) -> None:
        self.coordinate = coordinate
        self.size = BEAD
        self.contents = contents
        self.z_order = 2

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.draw.rect(self.coordinate.x - self.size/2, 
                         self.coordinate.y - self.size/2,
                         self.size, self.size, DWARF, 0)

        if self.contents:
            y_offset = -10
        else:
            y_offset = 0

        if show_labels:
            screen.draw.text("Room", 
                             center=(self.coordinate.x, self.coordinate.y + y_offset),
                             color = (255,255,255))

        if self.contents and show_labels:
            screen.draw.text(f"{self.contents}", 
                             center=(self.coordinate.x, self.coordinate.y - y_offset),
                             color = (255,255,255))

        if self.contents:
            self.contents.draw()


class Tunnel():
    def __init__(self, start: Location, end: Location, color: Tuple=CAVERN) -> None:
        self.start = start
        self.end = end
        self.color = color
        self.z_order = 1

    def update(self):
        pass

    def draw(self):
        screen.draw.line(self.color,
                         (self.start.coordinate.x, self.start.coordinate.y),
                         (self.end.coordinate.x, self.end.coordinate.y),
                         12)


def natural_cavern_factory() -> Cavern:
    coordinate = get_random_underground_location()

    tunnel = False
    tilt = 0
    contents = None
    cavern = Cavern(coordinate)

    detail = randint(1,6)
    match detail:
        case 1:
            cavern.tunnel = True
            cavern.tilt = randint(-FINGER//2, FINGER//2)
        case 2:
            cavern.contents = Entity(f"Plague {randint(1,4)}", cavern, (255,255,255))
        case 3:
            cavern.contents = Entity(f"Gemstones {randint(1,4)}", cavern, (255,255,255))
        case 4:
            pass
        case 5:
            cavern.contents = Entity(f"Primordial Beasts 1", cavern, (255,255,255))
        case 6:
            cavern.contents = Entity(f"Fate 1", cavern, (255,255,255))

    return cavern


def get_orbital_point(origin: PVector, radius: int, angle: int) -> PVector:
        new_x = radius * math.cos(math.radians(angle)) + origin.x
        new_y = radius * math.sin(math.radians(angle)) + origin.y
        return PVector(new_x, new_y)

def cave_complex_factory() -> List[Cavern | Tunnel]:
    radius = BEAD
    locations = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.contents = Entity("Primordial Beasts 1", cavern1, (255,255,255))
    locations.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, 3 * radius, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.contents = Entity("Primordial Beasts 1", cavern2, (255,255,255))
    locations.append(cavern2)

    angle_2 = angle_1 + randint(70,290)
    third_point = get_orbital_point(first_point, 3 * radius, angle_2)
    cavern3 = Cavern(third_point)
    cavern3.contents = Entity("Primordial Beasts 1", cavern3, (255,255,255))
    locations.append(cavern3)

    locations.append(Tunnel(locations[0], locations[1]))
    locations.append(Tunnel(locations[0], locations[2]))

    return locations

def ancient_wyrm_factory() -> List[Cavern | Tunnel]:
    radius = BEAD
    locations = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.contents = Entity("Ancient Wyrm 1", cavern1, (255,255,255))
    locations.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, radius * 1.5, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.contents = Entity("Treasure 1", cavern1, (255,255,255))
    locations.append(cavern2)

    locations.append(Tunnel(locations[0], locations[1]))

    return locations

def strata_depth(strata: int) -> int:
    return GROUND_LEVEL + STRATA_HEIGHT * strata + STRATA_HEIGHT//2

def update() -> None:
    for location in locations:
        location.update()

def draw() -> None:
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)

    back = [l for l in locations if l.z_order == 0]
    for location in back:
        location.draw()

    middle = [l for l in locations if l.z_order == 1]
    for location in middle:
        location.draw()

    front = [l for l in locations if l.z_order == 2]
    for location in front:
        location.draw()

    for i in range(6):
        screen.draw.text(f"{i+1}", center=(10, strata_depth(i)))
        screen.draw.text(f"{i+1}", center=(WIDTH-10, strata_depth(i)))

    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

    #print(screen.surface.get_at((WIDTH//2,HEIGHT//2)))

def add_caverns() -> None:
    locations.append(natural_cavern_factory())
    cavern_count = 1
    while randint(1,6) < 6 and cavern_count < 6:
        locations.append(natural_cavern_factory())
        cavern_count += 1

def dwarf_mine_factory(x_location: int, depth: int) -> List[Room | Tunnel]:
    locations = []

    locations.append(Room(PVector(x_location, GROUND_LEVEL)))
    
    half_height = (depth - GROUND_LEVEL)//2 + GROUND_LEVEL
    room1 = Room(PVector(x_location, half_height))
    room1.contents = Entity("Dwarves", room1, (255,255,255))
    locations.append(room1)

    room2 = Room(PVector(x_location, depth))
    room2.contents = Entity("Treasure", room2, (255,255,255))
    locations.append(room2)

    locations.append(Tunnel(locations[0], locations[1], DWARF))
    locations.append(Tunnel(locations[1], locations[2], DWARF))

    return locations

def get_y_at_x(start: PVector, end: PVector, x_coord: int) -> int:
        x1, y1 = start.x, start.y
        x2, y2 = end.x, end.y
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - (slope * x1)

        return slope * x_coord + intercept

# Primordial Age events
for i in range(3):
    check = randint(0,6)
    match check:
        case 0:
            locations.append(Mithril())
        case 1 | 2:
            add_caverns()
        case 3:
            locations.append(GoldVein())
        case 4:
            locations += cave_complex_factory()
        case 5:
            locations.append(UndergroundRiver())
        case 6:
            locations += ancient_wyrm_factory()
        # TO_DO: there is an additional choice for natural disasters,
        #        implement when we come to that rule

# Age of Civilization
# TO_DO: implmenting Dwarves first, Dark Elf to come later

# Dwarves
has_minerals = any(type(l) is Mithril or type(l) is GoldVein for l in locations)
if not has_minerals:
    print("Adding gold vein")
    locations.append(GoldVein())

# pick a spot on the surface above a gold vein or mithral deposit
minerals = [l for l in locations if type(l) is Mithril or type(l) is GoldVein]
selection = choice(minerals)
# TO_DO: alternatively, choose the mineral closest to the surface

x_location = 0
depth = 0
if isinstance(selection, Mithril):
    x_location = selection.center.x
    depth = selection.center.y

if isinstance(selection, GoldVein):
    if selection.left.y < selection.right.y:
        x_location = FINGER
        depth = get_y_at_x(selection.left, selection.right, x_location)
    elif selection.right.y < selection.left.y:
        x_location = WIDTH - FINGER
        depth = get_y_at_x(selection.left, selection.right, x_location)
    else:
        if randint(0,1) == 9:
            x_location = FINGER
            depth = get_y_at_x(selection.left, selection.right, x_location)
        else:
            x_location = WIDTH - FINGER
            depth = get_y_at_x(selection.left, selection.right, x_location)

locations += dwarf_mine_factory(x_location, depth)

run()
