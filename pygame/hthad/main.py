"""Play Tony Dowler's 'How to Host a Dungeon'."""
import math
from random import randint, choice, shuffle
from typing import List, Tuple, Callable, Any
from engine import screen, run
from pvector import PVector
from intersections import rect_segment_intersects
from location import Location, Cavern, Room
from entity import Entity
from landscape import Mithril, GoldVein, get_random_underground_location, strata_depth
from landscape import UndergroundRiver, Stratum
# pylint: disable=W0611
# W0611: Unused TITLE imported from constants (unused-import)
from constants import WIDTH, HEIGHT, TITLE, BEAD, GROUND_LEVEL, CAVERN
from constants import FINGER, CREATURE, EVENT, STRATA_HEIGHT, DWARF, TREASURE
from constants import ROOM_SPACING, GROUND, SKY, BORDER, WATER, SHOW_LABELS

locations = []

def check_for_connections(room: Location) -> None:
    """Test whether a newly-added room collides with an existing one, and link up if so."""
    cavities = [l for l in locations if isinstance(l, Location)]
    if room in cavities:
        cavities.remove(room)
    for location in cavities:
        if room.intersects(location):
            print(f"Intersection detected: {room} - {location}")
            room.add_neighbor(location)

def create_location(location_type: Callable, coordinate: PVector) -> Location:
    """Create a new location and add to the list."""
    new_location = location_type(coordinate)
    check_for_connections(new_location)
    return new_location

def get_all_entities() -> List[Entity]:
    """Return a list of all Entities on the map."""
    entities = []
    for location in locations:
        if isinstance(location, Location) and location.contents:
            entities.append(location.contents)
    return entities

def natural_cavern_factory() -> Cavern:
    """Generate a natural cavern."""
    coordinate = get_random_underground_location()

    cavern = create_location(Cavern, coordinate)
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
            cavern.contents = Entity("Primordial Beasts", cavern, CREATURE)
        case 6:
            cavern.contents = Entity("Fate", cavern, EVENT)

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
    cavern1 = create_location(Cavern, first_point)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Primordial Beasts", cavern1, CREATURE)
    sites.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, 3 * radius, angle_1)
    cavern2 = create_location(Cavern, second_point)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Primordial Beasts", cavern2, CREATURE)
    sites.append(cavern2)

    angle_2 = angle_1 + randint(70,290)
    third_point = get_orbital_point(first_point, 3 * radius, angle_2)
    cavern3 = create_location(Cavern, third_point)
    cavern3.color = CAVERN
    cavern3.contents = Entity("Primordial Beasts", cavern3, CREATURE)
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
    cavern1 = create_location(Cavern, first_point)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Ancient Wyrm", cavern1, CREATURE)
    sites.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, radius * 1.5, angle_1)
    cavern2 = create_location(Cavern, second_point)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Treasure", cavern2, TREASURE)
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

def dwarf_mine_factory(x_location: int, depth: int,
                       target_mineral: GoldVein | Mithril) -> List[Room]:
    """Generate the start of a Dwarf mine."""
    sites = []

    room0 = create_location(Room, PVector(x_location, GROUND_LEVEL))
    room0.name = "Start"
    room0.color = DWARF
    sites.append(room0)

    half_height = (depth - GROUND_LEVEL)//2 + GROUND_LEVEL
    room1 = create_location(Room, PVector(x_location, half_height))
    room1.name = "Barracks"
    room1.color = DWARF
    room1.contents = Entity("Dwarves", room1, CREATURE)
    sites.append(room1)

    room2 = create_location(Room, PVector(x_location, depth))
    room2.name = "Mine"
    room2.color = DWARF
    room2.target = target_mineral
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


colors = [(105,99,39),
          (137,131,75),
          (87,84,57),
          (177,169,96),
          (108,86,19),
          (125,117,93),
          (45,48,19)]
shuffle(colors)

strata = []
for i in range(6):
    strata.append(Stratum(150 + i * 120, colors[i]))


# TO_DO: need to keep track of yearly events

# Spring ~~~~~~~~
# gather all treasures connected to dwarf tunnels that are not dwarven treasures
# draw a new treasure room for each, or place in existing empty rooms
# for each treasure gathered, draw a barracks and put a dwarf creature in it,
# away from the mines


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
    room_to_add = create_location(Room, candidate_location)
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


class PrimordialAge():
    """Manages creation of the landscape and entities during the Primordial Age."""

    def __init__(self) -> None:
        """Create an instance of a PrimordialAge object."""
        self.rolls = 0

    def update(self) -> Any:
        """Return the next generated map location."""
        print("PrimordialAge.update()")
        return True

    def is_done(self) -> bool:
        """Return whether the PrimodialAge has completed or not."""
        return self.rolls >= 2

    # Primordial Age events
    def create_primordial_age(self) -> List:
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
                    for coord in river.caves:
                        new_cavern = create_location(Cavern, coord)
                        new_cavern.color = CAVERN
                        new_locations.append(new_cavern)
                case 6:
                    new_locations += ancient_wyrm_factory()
                # TO_DO: there is an additional choice for natural disasters,
                #        implement when we come to that rule
            self.rolls += 1

        return new_locations


class CivilizationAge():
    """Manages creation of the landscape and entities during the Age of Civilization."""

    def __init__(self) -> None:
        """Create an instance of a CivilizationAge object."""

    def update(self) -> Any:
        """Return the next generated map location."""
        print("CivilizationAge.update()")
        return False

    def is_done(self) -> bool:
        """Return whether the CivilizationAge has completed or not."""
        return False

    # Age of Civilization
    # TO_DO: implementing Dwarves first, Dark Elves to come later
    def age_of_civilization_setup(self):
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

        new_locations += dwarf_mine_factory(x_location, depth, target_mineral)
        return new_locations

counter = 1
current_stage = PrimordialAge()
next_stage = CivilizationAge()

locations += current_stage.create_primordial_age()
#locations += next_stage.age_of_civilization_setup()

mine_start = [r for r in locations if r.name == "Start"]
if mine_start:
    mine_start = mine_start[0]

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

            check_for_connections(new_room)

        # add another dwarf barracks and populate it - do this in separate loop because
        # these new arrivals should not be part of the treasure room bonanza above
        for treasure in treasures:
            # pylint: disable=C0103
            # C0103: Constant name doesn't conform to UPPER_CASE naming style (invalid-name)
            selection = get_parent_room(["Barracks", "Treasure Room"])
            new_room = get_candidate_room(selection, "Barracks")

            new_room.contents = Entity("Dwarves", new_room, CREATURE)

            check_for_connections(new_room)

    print(f"{mine_start.get_all_connected_locations()}")

    mines = [l for l in locations if l.name == "Mine"]
    deposit = mines[0].target

    if isinstance(deposit, GoldVein):
        direction = choice([-1,1])
        new_x = mines[0].coordinate.x + (direction * ROOM_SPACING)
        new_y = get_y_at_x(deposit.left, deposit.right, new_x)
        new_room = create_location(Room, PVector(new_x, new_y))
        new_room.color = mines[0].color
        mines[0].add_neighbor(new_room)
        new_room.contents = Entity("Treasure", new_room, TREASURE)
        locations.append(new_room)

    if isinstance(deposit, Mithril):
        # TO_DO: only works when the mine is centered on the deposit
        #        need a better approach here
        to_corner = PVector.mult(deposit.corner_vector, ROOM_SPACING)
        new_location = PVector.sub(mines[0].coordinate, to_corner)
        new_room = create_location(Room, new_location)
        new_room.color = mines[0].color
        mines[0].add_neighbor(new_room)
        new_room.contents = Entity("Treasure", new_room, TREASURE)
        locations.append(new_room)

print(get_all_entities())
creatures = [e for e in get_all_entities() if e.color == CREATURE]
print(creatures)

for location in locations:
    if isinstance(location, Location):
        reachables = [e for e in location.get_all_entities() if e.color == CREATURE]
        print(f"{location} => {reachables}")

def update() -> None:
    """Update game state once per frame."""
    global counter, locations, current_stage

    # probably want to make the Ages into a FSM
    if counter % 500 == 0:
        if current_stage.is_done():
            locations += next_stage.age_of_civilization_setup()
            current_stage = next_stage

    for location in locations:
        location.update()

    counter += 1

def draw() -> None:
    """Draw the game screen once per frame."""
    # pylint: disable=E1121
    # E1121: Too many positional arguments for method call
    #screen.draw.rect(0, GROUND_LEVEL, WIDTH, HEIGHT, GROUND, 0)
    for stratum in strata:
        stratum.draw()

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
# ---------------------------------------------
# We should generalize the pattern for creating a cave/room so we
# get consistent behavior, and can work out things like collisions
# in a uniform manner. Primordial age caves and the start of the
# dwarf mine don't obey the rules laid down later.
#
# In particular we should lay down one cave/room at a time, and check
# for collisions immediately. Then, if there is a connecting room to
# be generated as part of the cluster, test the tunnel first, then
# the new room.
#
# The compound creation functions should be broken up so we can
# do just one location at a time.
#
# Current steps (consolidated):
# 1) get a coordinate to place the location
#       get_random_underground_location()
#       get_orbital_point()
#       <determine x_location of mine>
#       get_parent_room()
#           get_candidate_room()
# 2) set color
# 3) set contents
# 4) embellishments (tunnels)
# 5) check for collisions/connections
# 6) if part of complex, add another per step 1 and connect
#
# ---------------------------------------------
# I'm contemplating compositing all the 'landscape' locations into a
# single bitmap. Ideally the locations list should only contain Caverns
# and Rooms.
#
# This meshes with the per-pixel ideas above. Treat every background image
# pixel as a resource unit. Currently we have dirt, mithril, gold and water.
#
# We'd need to change all the code that interacts with those location's
# coordinates. Drawing is easy - just draw the bitmap. For mine start, we
# could do ray-casting from the surface down until we strike a mineral. And
# so on.
#
# ---------------------------------------------
# How to handle interaction between the groups? I _think_ there's a pretty
# basic one-for-one attrition when groups meet, with only the larger
# group remaining. Probably some nuance, but that's a good place to start.
#
# So how about each update pass we check all entities to see if they can
# reach another team, then kill off the losers? We need:
#
# Tally all creature entities overall
# Clump together into groups (same name in same graph)
# Identify any graphs containing more than one group
# Eliminate entities accordingly
#
# By this logic, a graph shouldn't ever have more than two groups, right?
# Could there be some odd timing where this happens? A newly-added room
# tunnels into two different graphs simultaneously?
#
# ---------------------------------------------
# Another thought - it would be good to show the rooms/caves being added
# one by one. Technically they are, but it's too fast to see.
#
# I think we need to leverage the update() function. Use a counter to
# slow things down (so we invoke object.update() every 10 frames or
# whatever). At least two pulses I can think of right now:
#
# * Creation of new rooms
# * Interaction between creature groups
#
# So we'll need something to receive the update pulses. How about a class
# (or classes) to represent each game phase. Let's start with Primordial.

