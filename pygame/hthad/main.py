"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
from random import randint, choice
from typing import List, Tuple, Self
from pygame import Rect
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


class Location():
    def __init__(self, coordinate: PVector, name, color: Tuple) -> None:
        self.name = name
        self.color = color

        self.coordinate = coordinate
        self.size = BEAD
        self.rect = Rect(self.coordinate.x - self.size/2,
                         self.coordinate.y - self.size/2,
                         self.size, 
                         self.size)
        self.tunnels = []
        self.neighbors = []
        self.visited = False

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash((self.name, self.coordinate))

    def add_neighbor(self, neighbor: Self, bidi: bool=True) -> None:
        self.neighbors.append(neighbor)
        if bidi:
            neighbor.add_neighbor(self, False)

    # TO_DO: currently only works for Rooms, which are rects
    #        Caverns are circles, so we'll need to adjust
    def intersects(self, other: Self) -> bool:
        return self.rect.colliderect(other.rect)

    # TO_DO: generalize the BFS pattern
    def get_all_connected_locations(self) -> List:
        visited = [self]
        queue = [self]
        self.visited = True
       
        while queue:
            current_location = queue.pop(0)
       
            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True
       
        for location in visited:
            location.visited = False

        return visited

    def get_all_locations(self, location_name) -> List:
        locations = []
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)
            if current_location.name == location_name:
                locations.append(current_location)
       
            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True
       
        for location in visited:
            location.visited = False

        return locations

    def get_all_matching_entities(self, entity_name) -> List:
        entities = []
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)
            if current_location.contents and current_location.contents.name == entity_name:
                entities.append(current_location.contents)
       
            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True
       
        for location in visited:
            location.visited = False

        return entities

    def distance_to(self, goal) -> int:
        # need to consider case when location is not connected to self
        distances = { self : 0 }
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)

            if current_location == goal:
                break

            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    distances[neighbor] = distances[current_location] + 1
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True

        for location in visited:
            location.visited = False

        return distances[goal]     # I think we'll get a KeyError here if goal not in graph...


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


class Cavern(Location):
    def __init__(self, coordinate: PVector, contents: Entity=None, 
                 tunnel: bool=False, tilt: int=0, name: str="Cavern") -> None:
        super().__init__(coordinate, name, CAVERN)
        self.radius = self.size//2
        self.tunnel = tunnel        # TO_DO: confusing with graph edge tunnels
        self.tilt = tilt
        self.contents = contents

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.draw.circle(self.coordinate.x, self.coordinate.y, self.radius, self.color, 0)

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
            screen.draw.text(self.name, 
                             center=(self.coordinate.x, self.coordinate.y + y_offset),
                             color = (255,255,255))

        if self.contents and show_labels:
            screen.draw.text(f"{self.contents}", 
                             center=(self.coordinate.x, self.coordinate.y - y_offset),
                             color = (255,255,255))

        # TO_DO: we're drawing these twice, once from each direction...
        for n in self.neighbors:
            screen.draw.line(CAVERN,
                             (self.coordinate.x, self.coordinate.y),
                             (n.coordinate.x, n.coordinate.y),
                             12)
            # TO_DO: kludge to fix overdraw problem
            if n.contents:
                n.contents.draw()

        if self.contents:
            self.contents.draw()


class Room(Location):
    def __init__(self, coordinate: PVector, contents: Entity=None, name: str="Room") -> None:
        super().__init__(coordinate, name, DWARF)
        self.contents = contents

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.draw.rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h, self.color, 0)

        if self.contents:
            y_offset = -10
        else:
            y_offset = 0

        if show_labels:
            screen.draw.text(self.name, 
                             center=(self.coordinate.x, self.coordinate.y + y_offset),
                             color = (255,255,255))

        if self.contents and show_labels:
            screen.draw.text(f"{self.contents}", 
                             center=(self.coordinate.x, self.coordinate.y - y_offset),
                             color = (255,255,255))

        # TO_DO: we're drawing these twice, once from each direction...
        for n in self.neighbors:
            screen.draw.line(DWARF,
                             (self.coordinate.x, self.coordinate.y),
                             (n.coordinate.x, n.coordinate.y),
                             12)
            # TO_DO: kludge to fix overdraw problem
            if n.contents:
                n.contents.draw()

        if self.contents:
            self.contents.draw()


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

def update() -> None:
    for location in locations:
        location.update()

def draw() -> None:
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)

    for location in locations:
        location.draw()

    for i in range(6):
        screen.draw.text(f"{i+1}", center=(10, strata_depth(i)))
        screen.draw.text(f"{i+1}", center=(WIDTH-10, strata_depth(i)))

    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)


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
# TO_DO: implmenting Dwarves first, Dark Elf to come later
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

print(f"Distance = {room0.distance_to(room6)}\n")

mine_start = [r for r in locations if r.name == "Start"]
if mine_start:
    mine_start = mine_start[0]

# TO_DO: don't store all locations in locations list, we just need
#        one node (i.e. location) for each graph

if mine_start:
    treasures = mine_start.get_all_matching_entities("Treasure")
    dwarves = mine_start.get_all_matching_entities("Dwarves")

    if treasures:
        for treasure in treasures:
            # find a barracks to attach to
            selection = None
            barracks = mine_start.get_all_locations("Barracks")

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

            graph = selection.get_all_connected_locations()

            test = Room(PVector.sub(graph[-1].coordinate, PVector(5,5)))
            test.color = (255, 80, 80)
            locations.append(test)

            for location in graph:
                if candidate.intersects(location):
                    print(f"intersects {location}")
                if test.intersects(location):
                    print(f"intersects {location}")

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
