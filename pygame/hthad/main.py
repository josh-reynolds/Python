"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
from random import randint, choice
from typing import List, Tuple
from engine import screen, run
from pvector import PVector
from intersections import rect_segment_intersects
from location import Location, Cavern, Room
from entity import Entity
from landscape import Mithril, GoldVein, get_random_underground_location, strata_depth
from constants import WIDTH, HEIGHT, TITLE, BEAD, GROUND_LEVEL, CAVERN
from constants import FINGER, CREATURE, EVENT, STRATA_HEIGHT, DWARF, TREASURE
from constants import ROOM_SPACING, GROUND, SKY, BORDER, WATER, SHOW_LABELS

locations = []

# TO_DO: class accesses locations list, need to deal with this before moving
class UndergroundRiver():
    """Represents an underground river generated during the Primordial Age."""

    def __init__(self) -> None:
        """Create an UndergroundRiver object."""
        self.vertices = []

        self.lakes = []

        self.name = "Underground River"

        current_x = 0
        current_y = strata_depth(randint(0,5))

        while current_x < WIDTH and GROUND_LEVEL < current_y < HEIGHT and current_y:
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
                    locations.append(Cavern(PVector(current_x, current_y), CAVERN, None, False, 0))
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
        """Update the UndergroundRiver's state once per frame."""

    def draw(self) -> None:
        """Draw the UndergroundRiver once per frame."""
        for l in self.lakes:
            screen.draw.circle(l.x, l.y, BEAD, WATER, 0)

        for i,v in enumerate(self.vertices[:-1]):
            screen.draw.line(WATER,
                             (v.x, v.y),
                             (self.vertices[i+1].x, self.vertices[i+1].y),
                             8)
        if SHOW_LABELS:
            screen.draw.text(self.name, pos=(self.vertices[0].x, self.vertices[0].y))

def natural_cavern_factory() -> Cavern:
    """Generate a natural cavern."""
    coordinate = get_random_underground_location()

    cavern = Cavern(coordinate)
    cavern.color = CAVERN

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
            cavern.contents = Entity("Primordial Beasts 1", cavern, CREATURE)
        case 6:
            cavern.contents = Entity("Fate 1", cavern, EVENT)

    return cavern


def get_orbital_point(origin: PVector, radius: int, angle: int) -> PVector:
    """Generate a random point on a circle of given radius around an origin."""
    new_x = radius * math.cos(math.radians(angle)) + origin.x
    new_y = radius * math.sin(math.radians(angle)) + origin.y
    return PVector(new_x, new_y)

def cave_complex_factory() -> List[Cavern]:
    """Generate a cave complex."""
    radius = BEAD
    locations = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Primordial Beasts 1", cavern1, CREATURE)
    locations.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, 3 * radius, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Primordial Beasts 1", cavern2, CREATURE)
    locations.append(cavern2)

    angle_2 = angle_1 + randint(70,290)
    third_point = get_orbital_point(first_point, 3 * radius, angle_2)
    cavern3 = Cavern(third_point)
    cavern3.color = CAVERN
    cavern3.contents = Entity("Primordial Beasts 1", cavern3, CREATURE)
    locations.append(cavern3)

    locations[0].add_neighbor(locations[1])
    locations[0].add_neighbor(locations[2])

    return locations

# TO_DO: name the wyrm
def ancient_wyrm_factory() -> List[Cavern]:
    """Generate a cavern containing an ancient wyrm."""
    radius = BEAD
    locations = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Ancient Wyrm 1", cavern1, CREATURE)
    locations.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, radius * 1.5, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Treasure 1", cavern2, TREASURE)
    locations.append(cavern2)

    locations[0].add_neighbor(locations[1])

    return locations

def add_caverns() -> None:
    """Generate a random number of Caverns."""
    locations.append(natural_cavern_factory())
    cavern_count = 1
    while randint(1,6) < 6 and cavern_count < 6:
        locations.append(natural_cavern_factory())
        cavern_count += 1

def dwarf_mine_factory(x_location: int, depth: int) -> List[Room]:
    """Generate the start of a Dwarf mine."""
    locations = []

    room0 = Room(PVector(x_location, GROUND_LEVEL))
    room0.name = "Start"
    room0.color = DWARF
    locations.append(room0)

    half_height = (depth - GROUND_LEVEL)//2 + GROUND_LEVEL
    room1 = Room(PVector(x_location, half_height))
    room1.name = "Barracks"
    room1.color = DWARF
    room1.contents = Entity("Dwarves", room1, CREATURE)
    locations.append(room1)

    room2 = Room(PVector(x_location, depth))
    room2.name = "Mine"
    room2.color = DWARF
    room2.contents = Entity("Treasure", room2, TREASURE)
    locations.append(room2)

    locations[0].add_neighbor(locations[1])
    locations[1].add_neighbor(locations[2])

    return locations

# TO_DO: there's a vector-based solution for this too using
#        ratio of x along the line segment
def get_y_at_x(start: PVector, end: PVector, x_coord: int) -> int:
    """Calculate the y value of a point along a line at x."""
    x1, y1 = start.x, start.y
    x2, y2 = end.x, end.y
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (slope * x1)

    return slope * x_coord + intercept

# Primordial Age events
def create_primordial_age():
    """Generating Primordial Age map locations."""
    new_locations = []
    for _ in range(3):
        check = randint(0,6)
        match check:
            case 0:
                new_locations.append(Mithril())
            case 1 | 2:
                add_caverns()
            case 3:
                new_locations.append(GoldVein())
            case 4:
                new_locations += cave_complex_factory()
            case 5:
                new_locations.append(UndergroundRiver())
            case 6:
                new_locations += ancient_wyrm_factory()
            # TO_DO: there is an additional choice for natural disasters,
            #        implement when we come to that rule
    return new_locations

# Age of Civilization
# TO_DO: implementing Dwarves first, Dark Elves to come later
def age_of_civilization_setup():
    """Generating starting setup for the Age of Civilization map locations."""
    new_locations = []

    # Dwarves
    has_minerals = any(isinstance(l, (Mithril, GoldVein)) for l in locations)
    if not has_minerals:
        print("Adding gold vein")
        new_locations.append(GoldVein())

    # pick a spot on the surface above a gold vein or mithral deposit
    minerals = [l for l in locations if isinstance(l, (Mithril, GoldVein))]
    selection = choice(minerals + new_locations)
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

    new_locations += dwarf_mine_factory(x_location, depth)
    return new_locations

locations += create_primordial_age()
locations += age_of_civilization_setup()

# TO_DO: need to keep track of yearly events

# Spring ~~~~~~~~
# gather all treasures connected to dwarf tunnels that are not dwarven treasures
# draw a new treasure room for each, or place in existing empty rooms
# for each treasure gathered, draw a barracks and put a dwarf creature in it,
# away from the mines

# TEMPORARy GRAPHS for testing
#room0 = Room(PVector(250,200))
#room0.name = "Start"
#room0.color = DWARF
#locations.append(room0)
#
#room1 = Room(PVector(250,300))
#room1.name = "Barracks"
#room1.color = DWARF
#room1.contents = Entity("Dwarves", room1, CREATURE)
#locations.append(room1)
#
#room2 = Room(PVector(250,400))
#room2.name = "Mine 1"
#room2.color = DWARF
#room2.contents = Entity("Treasure", room2, TREASURE)
#locations.append(room2)
#
#room3 = Room(PVector(350,400))
#room3.name = "Mine 2"
#room3.color = DWARF
#room3.contents = Entity("Treasure", room3, TREASURE)
#locations.append(room3)
#
#room4 = Room(PVector(450,400))
#room4.name = "Barracks"
#room4.color = DWARF
#room4.contents = Entity("Dwarves", room4, CREATURE)
#locations.append(room4)
#
#room5 = Room(PVector(450,300))
#room5.name = "Treasure Room"
#room5.color = DWARF
#room5.contents = Entity("Dwarven Treasure", room5, TREASURE)
#locations.append(room5)
#
#room6 = Room(PVector(550,400))
#room6.name = "Barracks"
#room6.color = DWARF
#room6.contents = Entity("Dwarves", room6, CREATURE)
#locations.append(room6)
#
#room7 = Room(PVector(450,500))
#room7.name = "Barracks"
#room7.color = DWARF
#room7.contents = Entity("Dwarves", room7, CREATURE)
#locations.append(room7)
#
#room8 = Room(PVector(550,300))
#room8.name = "Barracks"
#room8.color = DWARF
#room8.contents = Entity("Dwarves", room8, CREATURE)
#locations.append(room8)
#
#room0.add_neighbor(room1)   # start -> barracks
#room1.add_neighbor(room2)   # barracks -> mine 1
#room1.add_neighbor(room3)   # barracks -> mine 2
#room2.add_neighbor(room3)   # mine 1 -> mine 2
#room3.add_neighbor(room4)   # mine 2 -> barracks
#room4.add_neighbor(room5)   # barracks -> treasure room
#room4.add_neighbor(room6)   # barracks -> barracks
#room4.add_neighbor(room7)   # barracks -> barracks
#room5.add_neighbor(room8)   # treasure room -> barracks

mine_start = [r for r in locations if r.name == "Start"]
if mine_start:
    mine_start = mine_start[0]

# TO_DO: don't store all locations in locations list, we just need
#        one node (i.e. location) for each graph

directions = [PVector(ROOM_SPACING,0),
              PVector(-ROOM_SPACING,0),
              PVector(0,ROOM_SPACING),
              PVector(0,-ROOM_SPACING),
              PVector(ROOM_SPACING,ROOM_SPACING),
              PVector(-ROOM_SPACING,ROOM_SPACING),
              PVector(ROOM_SPACING,-ROOM_SPACING),
              PVector(-ROOM_SPACING,-ROOM_SPACING)]

def add_candidate(name: str, selection: Location, direction: int) -> Location:
    """Add a candidate location to the locations list."""
    candidate_location = PVector.add(selection.coordinate, directions[direction])
    candidate = Room(candidate_location)
    candidate.name = name
    locations.append(candidate)
    return candidate

def is_viable(candidate: Location, rooms: List[Location], tunnels: List[Tuple]) -> bool:
    """Test whether a candidate location is legal."""
    for location in rooms:
        if candidate.intersects(location):
            return False

    tunnel_coords = [(a.coordinate, b.coordinate) for a,b in tunnels]
    for tunnel in tunnel_coords:
        if rect_segment_intersects(candidate.rect, tunnel):
            viable = False

    if out_of_bounds(candidate.coordinate):
        return False

    return True

def in_bounds(point: PVector) -> bool:
    """Test whether the given point is within the underground region of the screen."""
    return 0 <= point.x <= WIDTH and GROUND_LEVEL <= point.y <= HEIGHT

def out_of_bounds(point: PVector) -> bool:
    """Test whether the given point is outside the underground region of the screen."""
    return not in_bounds(point)

# start with priority-sorted list of parent locations
# take the first one
#   test candidate locations attached to parent for viability
#   bail out after some number of attempts?
# try another if none found
# how do we handle if _no_ viable locations can be found?

if mine_start:
    treasures = mine_start.get_all_matching_entities("Treasure")

    if treasures:
        for treasure in treasures:
            selection = None
            barracks = mine_start.get_locations_by_name("Barracks")

            neighbor_counts = [len(b.neighbors) for b in barracks]
            min_neighbors = min(neighbor_counts)

            first_cut = [b for b in barracks if len(b.neighbors) == min_neighbors]

            candidates = sorted(barracks, key=lambda entry: len(entry.neighbors))
            print(candidates)

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

            attempt = 0
            while attempt < 8:
                candidate = add_candidate("Treasure Room", selection, attempt)

                rooms = selection.get_all_connected_locations()
                tunnels = selection.get_all_connected_tunnels()

                viable = is_viable(candidate, rooms, tunnels)

                # TO_DO: tunnel crossing aren't handled yet
                # TO_DO: intersections with caverns not handled yet

                if viable:
                    print("Candidate location is viable - adding room.")
                    selection.add_neighbor(candidate)
                    candidate.color = selection.color
                    treasure.parent = candidate
                    treasure.name = "Dwarven Treasure"
                    candidate.contents = treasure

                    distances = [PVector.dist(candidate.coordinate, r.coordinate) for r in rooms]
                    dist_to_parent = PVector.dist(candidate.coordinate, selection.coordinate)

                    for i,room in enumerate(rooms):
                        if distances[i] <= dist_to_parent:
                            room.add_neighbor(candidate)

                    attempt = 8
                else:
                    locations.remove(candidate)
                    attempt += 1

        # add another dwarf barracks and populate it - do this in separate
        # loop because these new arrivals should not be part of the treasure
        # room bonanza above
        for treasure in treasures:
            # new barracks should attach to any non-mine room
            # preference for fewest neighbors
            # no other criteria - this can be anywhere in the complex
            # find a non-intersecting location
            # place a barracks there
            # add a dwarf to the barracks
            # same special cases as above for treasure rooms - in
            # fact we should extract a "get new room" function here
            selection = None
            rooms = mine_start.get_locations_by_name("Barracks")
            rooms += mine_start.get_locations_by_name("Treasure Room")

            neighbor_counts = [len(r.neighbors) for r in rooms]
            min_neighbors = min(neighbor_counts)

            selection = choice([r for r in rooms if len(r.neighbors) == min_neighbors])

            attempt = 0
            while attempt < 8:
                candidate = add_candidate("Barracks", selection, attempt)

                rooms = selection.get_all_connected_locations()
                tunnels = selection.get_all_connected_tunnels()

                viable = is_viable(candidate, rooms, tunnels)

                # TO_DO: tunnel crossing aren't handled yet
                # TO_DO: intersections with caverns not handled yet

                if viable:
                    print("Candidate location is viable - adding room.")
                    selection.add_neighbor(candidate)
                    candidate.color = selection.color
                    candidate.contents = Entity("Dwarves", candidate, CREATURE)

                    distances = [PVector.dist(candidate.coordinate, r.coordinate) for r in rooms]
                    dist_to_parent = PVector.dist(candidate.coordinate, selection.coordinate)

                    for i,room in enumerate(rooms):
                        if distances[i] <= dist_to_parent:
                            room.add_neighbor(candidate)

                    attempt = 8
                else:
                    locations.remove(candidate)
                    attempt += 1

def update() -> None:
    """Update game state once per frame."""
    for location in locations:
        location.update()

def draw() -> None:
    """Draw the game screen once per frame."""
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)

    for location in locations:
        location.draw()

    for i in range(6):
        screen.draw.text(f"{i+1}", center=(10, strata_depth(i)))
        screen.draw.text(f"{i+1}", center=(WIDTH-10, strata_depth(i)))

    screen.draw.rect(0, 0, WIDTH, GROUND_LEVEL, SKY, 0)
    screen.draw.line(BORDER, (0, GROUND_LEVEL), (WIDTH, GROUND_LEVEL), 2)

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
