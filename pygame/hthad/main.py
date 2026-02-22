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
from landscape import UndergroundRiver
# pylint: disable=W0611
# W0611: Unused TITLE imported from constants (unused-import)
from constants import WIDTH, HEIGHT, TITLE, BEAD, GROUND_LEVEL, CAVERN
from constants import FINGER, CREATURE, EVENT, STRATA_HEIGHT, DWARF, TREASURE
from constants import ROOM_SPACING, GROUND, SKY, BORDER, WATER, SHOW_LABELS

locations = []

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
    """Generate a point on a circle of given radius and angle around an origin."""
    new_x = radius * math.cos(math.radians(angle)) + origin.x
    new_y = radius * math.sin(math.radians(angle)) + origin.y
    return PVector(new_x, new_y)

def cave_complex_factory() -> List[Cavern]:
    """Generate a cave complex."""
    radius = BEAD
    sites = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Primordial Beasts 1", cavern1, CREATURE)
    sites.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, 3 * radius, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Primordial Beasts 1", cavern2, CREATURE)
    sites.append(cavern2)

    angle_2 = angle_1 + randint(70,290)
    third_point = get_orbital_point(first_point, 3 * radius, angle_2)
    cavern3 = Cavern(third_point)
    cavern3.color = CAVERN
    cavern3.contents = Entity("Primordial Beasts 1", cavern3, CREATURE)
    sites.append(cavern3)

    sites[0].add_neighbor(sites[1])
    sites[0].add_neighbor(sites[2])

    return sites

# TO_DO: name the wyrm
def ancient_wyrm_factory() -> List[Cavern]:
    """Generate a cavern containing an ancient wyrm."""
    radius = BEAD
    sites = []

    first_point = get_random_underground_location()
    cavern1 = Cavern(first_point)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Ancient Wyrm 1", cavern1, CREATURE)
    sites.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, radius * 1.5, angle_1)
    cavern2 = Cavern(second_point)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Treasure 1", cavern2, TREASURE)
    sites.append(cavern2)

    sites[0].add_neighbor(sites[1])

    return sites

def add_caverns() -> None:
    """Generate a random number of Caverns."""
    locations.append(natural_cavern_factory())
    cavern_count = 1
    while randint(1,6) < 6 and cavern_count < 6:
        locations.append(natural_cavern_factory())
        cavern_count += 1

def dwarf_mine_factory(x_location: int, depth: int) -> List[Room]:
    """Generate the start of a Dwarf mine."""
    sites = []

    room0 = Room(PVector(x_location, GROUND_LEVEL))
    room0.name = "Start"
    room0.color = DWARF
    sites.append(room0)

    half_height = (depth - GROUND_LEVEL)//2 + GROUND_LEVEL
    room1 = Room(PVector(x_location, half_height))
    room1.name = "Barracks"
    room1.color = DWARF
    room1.contents = Entity("Dwarves", room1, CREATURE)
    sites.append(room1)

    room2 = Room(PVector(x_location, depth))
    room2.name = "Mine"
    room2.color = DWARF
    room2.contents = Entity("Treasure", room2, TREASURE)
    sites.append(room2)

    sites[0].add_neighbor(sites[1])
    sites[1].add_neighbor(sites[2])

    return sites

# TO_DO: there's a vector-based solution for this too using
#        ratio of x along the line segment
def get_y_at_x(start: PVector, end: PVector, x_coord: int) -> int:
    """Calculate the y value of a point along a line at x."""
    x_1, y_1 = start.x, start.y
    x_2, y_2 = end.x, end.y
    slope = (y_2 - y_1) / (x_2 - x_1)
    intercept = y_1 - (slope * x_1)

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
                river = UndergroundRiver()
                new_locations.append(river)
                for cave in river.caves:
                    new_locations.append(cave)
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
    target_mineral = choice(minerals + new_locations)
    # TO_DO: alternatively, choose the mineral closest to the surface

    x_location = 0
    depth = 0
    if isinstance(target_mineral, Mithril):
        x_location = target_mineral.center.x
        depth = target_mineral.center.y

    if isinstance(target_mineral, GoldVein):
        if target_mineral.left.y < target_mineral.right.y:
            x_location = FINGER
            depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)
        elif target_mineral.right.y < target_mineral.left.y:
            x_location = WIDTH - FINGER
            depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)
        else:
            if randint(0,1) == 9:
                x_location = FINGER
                depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)
            else:
                x_location = WIDTH - FINGER
                depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)

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

def add_candidate(name: str, parent: Location, direction: int) -> Location:
    """Add a candidate location to the locations list."""
    candidate_location = PVector.add(parent.coordinate, directions[direction])
    room_to_add = Room(candidate_location)
    room_to_add.name = name
    locations.append(room_to_add)
    return room_to_add

def is_viable(candidate_room: Location, nodes: List[Location], edges: List[Tuple]) -> bool:
    """Test whether a candidate location is legal."""
    for location in nodes:
        if candidate_room.intersects(location):
            return False

    tunnel_coords = [(a.coordinate, b.coordinate) for a,b in edges]
    for tunnel in tunnel_coords:
        if rect_segment_intersects(candidate_room.rect, tunnel):
            return False

    if out_of_bounds(candidate_room.coordinate):
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

def get_parent_room(types: List[str]) -> Location:
    """Return the parent room to attach a new room to."""
    parents = []
    for room_name in types:
        parents += mine_start.get_locations_by_name(room_name)

    neighbor_counts = [len(r.neighbors) for r in parents]
    min_neighbors = min(neighbor_counts)

    return choice([r for r in parents if len(r.neighbors) == min_neighbors])

def get_candidate_room(parent: Location, room_name: str) -> Location | None:
    """Evaluate potental candidate Locations and return first viable."""
    attempt = 0
    while attempt < 8:
        candidate = add_candidate(room_name, parent, attempt)

        rooms = parent.get_all_connected_locations()
        tunnels = parent.get_all_connected_tunnels()

        viable = is_viable(candidate, rooms, tunnels)

        # TO_DO: tunnel crossings aren't handled yet
        # TO_DO: intersections with caverns aren't handled yet

        if viable:
            print("Candidate location is viable - adding room.")
            parent.add_neighbor(candidate)
            candidate.color = parent.color
            distances = [PVector.dist(candidate.coordinate, r.coordinate) for r in rooms]
            dist_to_parent = PVector.dist(candidate.coordinate, parent.coordinate)

            for i,room in enumerate(rooms):
                if distances[i] <= dist_to_parent:
                    room.add_neighbor(candidate)

            return candidate

        locations.remove(candidate)
        attempt += 1

    return None

if mine_start:
    treasures = mine_start.get_all_matching_entities("Treasure")

    if treasures:
        for treasure in treasures:
            # pylint: disable=C0103
            # C0103: Constant name doesn't conform to UPPER_CASE naming style (invalid-name)
            selection = get_parent_room(["Barracks"])
            new_room = get_candidate_room(selection, "Treasure Room")

            treasure.parent = new_room
            treasure.name = "Dwarven Treasure"
            new_room.contents = treasure

            cavities = [l for l in locations if isinstance(l, Location)]
            cavities.remove(new_room)
            for location in cavities:
                if new_room.intersects(location):
                    print(f"Intersection detected: {new_room} - {location}")
                    new_room.add_neighbor(location)

        # add another dwarf barracks and populate it - do this in separate loop because
        # these new arrivals should not be part of the treasure room bonanza above
        for treasure in treasures:
            # pylint: disable=C0103
            # C0103: Constant name doesn't conform to UPPER_CASE naming style (invalid-name)
            selection = get_parent_room(["Barracks", "Treasure Room"])
            new_room = get_candidate_room(selection, "Barracks")

            new_room.contents = Entity("Dwarves", new_room, CREATURE)

            cavities = [l for l in locations if isinstance(l, Location)]
            cavities.remove(new_room)
            for location in cavities:
                if new_room.intersects(location):
                    print(f"Intersection detected: {new_room} - {location}")
                    new_room.add_neighbor(location)

    print(f"{mine_start.get_all_connected_locations()}")

def update() -> None:
    """Update game state once per frame."""
    for location in locations:
        location.update()

def draw() -> None:
    """Draw the game screen once per frame."""
    # pylint: disable=E1121
    # E1121: Too many positional arguments for method call
    screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)

    for location in locations:
        location.draw()

    for index in range(6):
        screen.draw.text(f"{index+1}", center=(10, strata_depth(index)))
        screen.draw.text(f"{index+1}", center=(WIDTH-10, strata_depth(index)))

    # pylint: disable=E1121
    # E1121: Too many positional arguments for method call
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
