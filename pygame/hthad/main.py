"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
from random import randint, choice
from typing import List, Tuple, Self
from pygame import Rect, mouse
from engine import screen, run
from pvector import PVector
from screen_matrix import push_matrix, pop_matrix, line, rotate, translate
from screen_matrix import equilateral_triangle
from location import Location, Cavern, Room

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
GOLD = (255, 255, 0)
BORDER = (0, 0, 0)
CAVERN = (0, 0, 0)
WATER = (0, 0, 255)
DWARF = (100, 80, 255)

TREASURE = (255,255,0)
CREATURE = (255,0,255)
EVENT = (128,128,128)

show_labels = False

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

def segments_intersect(line_1: Tuple[PVector, PVector], line_2: Tuple[PVector, PVector]) -> bool:
    r = PVector.sub(line_1[1], line_1[0])
    s = PVector.sub(line_2[1], line_2[0])

    n = PVector.sub(line_2[0], line_1[0])

    u_numerator = n.cross(r)
    denominator = r.cross(s)

    if u_numerator == 0 and denominator == 0:
        # collinear case

        # endpoints touch
        if (line_1[0] == line_2[0] or line_1[0] == line_2[1] 
            or line_1[1] == line_2[0] or line_1[1] == line_2[1]):
            return True

        # overlapping segments
        # segments overlap if their projection onto the x axis overlap
        # (or y axis if lines are vertical)

        # projection of AB is:
        # [min(A.x, B.x), max(A.x, B.x)]

        if line_1[0].x != line_1[1].x:     # lines are not vertical
            projection_1 = (min(line_1[0].x, line_1[1].x),
                            max(line_1[0].x, line_1[1].x))

            projection_2 = (min(line_2[0].x, line_2[1].x),
                            max(line_2[0].x, line_2[1].x))

        else:
            projection_1 = (min(line_1[0].y, line_1[1].y),
                            max(line_1[0].y, line_1[1].y))

            projection_2 = (min(line_2[0].y, line_2[1].y),
                            max(line_2[0].y, line_2[1].y))

        return projection_1[0] < projection_2[1] and projection_1[1] > projection_2[0]


    if denominator == 0:
        # parallel case
        return False

    u = u_numerator / denominator
    t = n.cross(s) / denominator

    return t >= 0 and t <= 1 and u >= 0 and u <= 1

def rect_segment_intersects(rect: Rect, segment: Tuple) -> bool:
    top_left = PVector(rect.x, rect.y)
    top_right = PVector(rect.x + rect.w, rect.y)
    bottom_right = PVector(rect.x + rect.w, rect.y + rect.h)
    bottom_left = PVector(rect.x, rect.y + rect.h)

    top = (top_left, top_right)
    right = (top_right, bottom_right)
    bottom = (bottom_right, bottom_left)
    left = (bottom_left, top_left)

    result = False
    for edge in (top, right, bottom, left):
        if segments_intersect(edge, segment):
            result = True

    return result


class Mithril():
    def __init__(self) -> None:
        self.center = get_random_underground_location()
        self.radius = FINGER // 2
        self.corner = nearest_corner(self.center)

        corner_vector = PVector.normalize(PVector.sub(self.center, self.corner))
        self.angle = math.radians(corner_vector.heading()) + math.pi

        self.name = "Mithril"

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
            screen.draw.text(self.name, center=(self.center.x, self.center.y))


class UndergroundRiver():
    def __init__(self) -> None:
        self.vertices = []

        self.caves = []
        self.lakes = []

        self.name = "Underground River"
        
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
            screen.draw.text(self.name, pos=(self.vertices[0].x, self.vertices[0].y))

class GoldVein():
    def __init__(self) -> None:
        self.left = PVector(0, strata_depth(randint(0,5)))
        self.right = PVector(WIDTH, strata_depth(randint(0,5)))
        self.midpoint = PVector(WIDTH//2, 
                                (self.right.y - self.left.y)//2 + self.left.y)
        self.name = "Gold Vein"

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.draw.line(GOLD, 
                         (self.left.x, self.left.y),
                         (self.right.x, self.right.y),
                         8)
        if show_labels:
            screen.draw.text(self.name, center=(self.midpoint.x, self.midpoint.y))


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

    def __repr__(self) -> str:
        return f"{self.name} ({self.parent})"

    def draw(self) -> None:
        screen.draw.circle(self.x, self.y, self.radius, self.color, 0)


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
            cavern.contents = Entity(f"Plague {randint(1,4)}", cavern, EVENT)
        case 3:
            cavern.contents = Entity(f"Gemstones {randint(1,4)}", cavern, TREASURE)
        case 4:
            pass
        case 5:
            cavern.contents = Entity(f"Primordial Beasts 1", cavern, CREATURE)
        case 6:
            cavern.contents = Entity(f"Fate 1", cavern, EVENT)

    return cavern


def get_orbital_point(origin: PVector, radius: int, angle: int) -> PVector:
        new_x = radius * math.cos(math.radians(angle)) + origin.x
        new_y = radius * math.sin(math.radians(angle)) + origin.y
        return PVector(new_x, new_y)

def cave_complex_factory() -> List[Cavern]:
    radius = BEAD
    locations = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.contents = Entity("Primordial Beasts 1", cavern1, CREATURE)
    locations.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, 3 * radius, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.contents = Entity("Primordial Beasts 1", cavern2, CREATURE)
    locations.append(cavern2)

    angle_2 = angle_1 + randint(70,290)
    third_point = get_orbital_point(first_point, 3 * radius, angle_2)
    cavern3 = Cavern(third_point)
    cavern3.contents = Entity("Primordial Beasts 1", cavern3, CREATURE)
    locations.append(cavern3)

    locations[0].add_neighbor(locations[1])
    locations[0].add_neighbor(locations[2])

    return locations

# TO_DO: name the wyrm
def ancient_wyrm_factory() -> List[Cavern]:
    radius = BEAD
    locations = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.contents = Entity("Ancient Wyrm 1", cavern1, CREATURE)
    locations.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, radius * 1.5, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.contents = Entity("Treasure 1", cavern2, TREASURE)
    locations.append(cavern2)

    locations[0].add_neighbor(locations[1])

    return locations

def strata_depth(strata: int) -> int:
    return GROUND_LEVEL + STRATA_HEIGHT * strata + STRATA_HEIGHT//2

def add_caverns() -> None:
    locations.append(natural_cavern_factory())
    cavern_count = 1
    while randint(1,6) < 6 and cavern_count < 6:
        locations.append(natural_cavern_factory())
        cavern_count += 1

def dwarf_mine_factory(x_location: int, depth: int) -> List[Room]:
    locations = []

    room0 = Room(PVector(x_location, GROUND_LEVEL))
    room0.name = "Start"
    locations.append(room0)
    
    half_height = (depth - GROUND_LEVEL)//2 + GROUND_LEVEL
    room1 = Room(PVector(x_location, half_height))
    room1.name = "Barracks"
    room1.contents = Entity("Dwarves", room1, CREATURE)
    locations.append(room1)

    room2 = Room(PVector(x_location, depth))
    room2.name = "Mine"
    room2.contents = Entity("Treasure", room2, TREASURE)
    locations.append(room2)

    locations[0].add_neighbor(locations[1])
    locations[1].add_neighbor(locations[2])

    return locations

# TO_DO: there's a vector-based solution for this too using
#        ratio of x along the line segment
def get_y_at_x(start: PVector, end: PVector, x_coord: int) -> int:
        x1, y1 = start.x, start.y
        x2, y2 = end.x, end.y
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - (slope * x1)

        return slope * x_coord + intercept

# Primordial Age events
def create_primordial_age():
    global locations
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
# TO_DO: implementing Dwarves first, Dark Elves to come later
def age_of_civilization_setup():
    global locations

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

#create_primordial_age()
#age_of_civilization_setup()

# TO_DO: need to keep track of yearly events

# Spring ~~~~~~~~
# gather all treasures connected to dwarf tunnels that are not dwarven treasures
# draw a new treasure room for each, or place in existing empty rooms
# for each treasure gathered, draw a barracks and put a dwarf creature in it,
# away from the mines

# TEMPORARy GRAPHS for testing
room0 = Room(PVector(250,200))
room0.name = "Start"
locations.append(room0)

room1 = Room(PVector(250,300))
room1.name = "Barracks"
room1.contents = Entity("Dwarves", room1, CREATURE)
locations.append(room1)

room2 = Room(PVector(250,400))
room2.name = "Mine 1"
room2.contents = Entity("Treasure", room2, TREASURE)
locations.append(room2)

room3 = Room(PVector(350,400))
room3.name = "Mine 2"
room3.contents = Entity("Treasure", room3, TREASURE)
locations.append(room3)

room4 = Room(PVector(450,400))
room4.name = "Barracks"
room4.contents = Entity("Dwarves", room4, CREATURE)
locations.append(room4)

room5 = Room(PVector(450,300))
room5.name = "Treasure Room"
room5.contents = Entity("Dwarven Treasure", room5, TREASURE)
locations.append(room5)

room6 = Room(PVector(550,400))
room6.name = "Barracks"
room6.contents = Entity("Dwarves", room6, CREATURE)
locations.append(room6)

room7 = Room(PVector(450,500))
room7.name = "Barracks"
room7.contents = Entity("Dwarves", room7, CREATURE)
locations.append(room7)

room8 = Room(PVector(550,300))
room8.name = "Barracks"
room8.contents = Entity("Dwarves", room8, CREATURE)
locations.append(room8)

room0.add_neighbor(room1)   # start -> barracks
room1.add_neighbor(room2)   # barracks -> mine 1
room1.add_neighbor(room3)   # barracks -> mine 2
room2.add_neighbor(room3)   # mine 1 -> mine 2
room3.add_neighbor(room4)   # mine 2 -> barracks
room4.add_neighbor(room5)   # barracks -> treasure room
room4.add_neighbor(room6)   # barracks -> barracks
room4.add_neighbor(room7)   # barracks -> barracks
room5.add_neighbor(room8)   # treasure room -> barracks

cursor = Room(PVector(WIDTH//2, HEIGHT//2))
cursor.name = "Cursor"
cursor.color = (200,200,0)
locations.append(cursor)

mine_start = [r for r in locations if r.name == "Start"]
if mine_start:
    mine_start = mine_start[0]

# TO_DO: don't store all locations in locations list, we just need
#        one node (i.e. location) for each graph

if mine_start:
    treasures = mine_start.get_all_matching_entities("Treasure")

    if treasures:
        for treasure in treasures:
            # find a barracks to attach to
            selection = None
            barracks = mine_start.get_locations_by_name("Barracks")

            neighbor_counts = [len(b.neighbors) for b in barracks]
            min_neighbors = min(neighbor_counts)

            first_cut = [b for b in barracks if len(b.neighbors) == min_neighbors]

            if len(first_cut) > 1:
                distances = [b.distance_to(treasure.parent) for b in first_cut]
                min_distance = min(distances)

                second_cut = [b for b in first_cut 
                              if b.distance_to(treasure.parent) == min_distance]

                if len(second_cut) > 1:
                    selection = choice(second_cut)
                else:
                    selection = second_cut[0]
            else:
                selection = first_cut[0]

            print(selection)

            # we'll probably have a bunch of potential sites, and
            # test until we find winner - order the list by priority,
            # horizontal first, then vertical, then at an angle
            candidate_location = PVector.add(selection.coordinate, PVector(100,0))

            candidate = Room(candidate_location)
            candidate.name = "Test"
            print(candidate.coordinate)
            locations.append(candidate)

            rooms = selection.get_all_connected_locations()
            print(f"{len(rooms)} rooms in graph")

            test = Room(PVector.sub(rooms[-1].coordinate, PVector(5,5)))
            test.color = (255, 80, 80)
            locations.append(test)

            viable = True
            for location in rooms:
                if candidate.intersects(location):
                    viable = False
                if test.intersects(location):
                    print(f"intersects {location}")

            tunnels = selection.get_all_connected_tunnels()
            print(tunnels)
            print(f"{len(tunnels)} tunnels in graph")

            tunnel_coords = [(a.coordinate, b.coordinate) for a,b in tunnels]
            print(tunnel_coords)

            for tunnel in tunnel_coords:
                if rect_segment_intersects(candidate.rect, tunnel):
                    print(f"{tunnel} intersects {candidate}")



            # for room in graph:
            #    if candidate.intersect(room):
            #        reject

            # remove treasure
            #    straightforward
            #
            # create a new treasure room
            #    find a barracks to attach to
            #       get all barracks
            #       first priority - barracks w/ least neighbors
            #       second priority - closest barracks to mine source
            #       random choice if still tied
            #
            #    find a non-intersecting location
            #       choose a point far enough away to not intersect barracks
            #       priority to horizontal & vertical connections
            #       treasure room cannot overlap existing dwarf rooms
            #       treasure room cannot overlap existing dwarf tunnels
            #       same applies to Barracks -> Treasure Room tunnel, no crossings
            #       we only check dwarf locations - we *can* intersect caverns
            #       TBD what happens in that case...
            #       
            #    add & connect the treasure room
            #       straightforward
            #
            # add a dwarven treasure to treasure room
            #    straightforward


#line_a = (PVector(800, 500), PVector(900, 400))
#line_b = (PVector(700, 600), PVector(850, 650))

# 1100 x 850
lines = [(PVector(550, 100), PVector(550, 750)),
         (PVector(100, 425), PVector(1000, 425))]

rect_a = Rect(10, 110, 100, 100)

rects = [Rect(540,90,20,20),
         Rect(90,415,20,20),
         Rect(540,415,20,20),
         Rect(990,415,20,20),
         Rect(540,740,20,20),
         ]

for rect in rects:
    print(f"\nChecking {rect}")
    for line in lines:
        if rect_segment_intersects(rect, line):
            print(f"{line} intersects {rect}")


def update() -> None:
    global rect
    #global line_b
    cursor.coordinate = PVector(*mouse.get_pos())
    rect_a.x = cursor.coordinate.x - rect_a.w/2
    rect_a.y = cursor.coordinate.y - rect_a.h/2
    #line_b = (line_b[0], cursor.coordinate)

    #for location in locations:
        #location.update()
#
        #if cursor.intersects(location):
            #location.color = (255,0,0)
        #else:
            #location.color = DWARF
#
    #tunnels = locations[0].get_all_connected_tunnels()
    #tunnel_coords = [(a.coordinate, b.coordinate) for a,b in tunnels]
#
    #for tunnel in tunnel_coords:
        #if rect_segment_intersects(cursor.rect, tunnel):
            #print(f"{tunnel} intersects {cursor}")

    #print(f"{segments_intersect(line_a, line_b)}")

    #for line in lines:
        #if rect_segment_intersects(rect, line):
            #print(f"{line} intersects")

def draw() -> None:
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)

    #for location in locations:
        #location.draw()

    for i in range(6):
        screen.draw.text(f"{i+1}", center=(10, strata_depth(i)))
        screen.draw.text(f"{i+1}", center=(WIDTH-10, strata_depth(i)))

    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

    #screen.draw.line(BORDER, (line_a[0].x, line_a[0].y), (line_a[1].x, line_a[1].y), 8)
    #screen.draw.line(BORDER, (line_b[0].x, line_b[0].y), (line_b[1].x, line_b[1].y), 8)

    screen.draw.rect(rect_a.x, rect_a.y, rect_a.h, rect_a.w, (255,0,0), 1)

    for rect in rects:
        screen.draw.rect(rect.x, rect.y, rect.h, rect.w, (255,0,255), 1)

    for line in lines:
        screen.draw.line(BORDER, (line[0].x, line[0].y), (line[1].x, line[1].y), 4)

run()

# ---------------------------------------------
# May want to keep the spirit of the original rather than try to exactly
# duplicate - it's a bunch of analog pen-on-paper mechanics, and a lot of
# things are left as aesthetic judgement calls on the part of the player.
#
# Also the rules are very handwavy about a lot of things. Will need to
# make decisions how to handle.
#
# Random ideas:
#
# What if the tailings from mining are gathered and need to go somewhere,
# like a heap on the surface?
#
# I was envisioning mining involving grabbing all the pixels under the
# mine square and treating each one as an entity - either dirt, water,
# gold or mithril right now.

# print(screen.surface.get_at((WIDTH//2,HEIGHT//2)))

# OPEN QUESTIONS
# How to handle collisions during the Primordial and Civilization setup phases?

# ---------------------------------------------
# line segment - rectangle intersection:
#   check intersection of line segment with each side of rectangle
#   special case: line segment entirely within rectangle
#
# line segment intersection:
#   see Stack Overflow 563198
# 
