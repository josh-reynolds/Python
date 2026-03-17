"""Contains the CivilizationAge class and supporting functions."""
from random import choice, randint, shuffle
from typing import List, Tuple
from pygame import Rect
from pvector import PVector
from constants import FINGER, WIDTH, ROOM_SPACING, BEAD, GROUND_LEVEL, DWARF, CREATURE
from constants import TREASURE, HEIGHT
from entity import Entity
from landscape import Mithril, GoldVein
from location import Location, Room
from location_strategy import LocationStrategy
from utilities import create_location, check_for_connections, is_viable

directions = [PVector(ROOM_SPACING,0),
              PVector(-ROOM_SPACING,0),
              PVector(0,ROOM_SPACING),
              PVector(0,-ROOM_SPACING),
              PVector(ROOM_SPACING,ROOM_SPACING),
              PVector(-ROOM_SPACING,ROOM_SPACING),
              PVector(ROOM_SPACING,-ROOM_SPACING),
              PVector(-ROOM_SPACING,-ROOM_SPACING)]

def add_candidate(name: str, parent: Location, direction: int,
                  locs: List[Location],
                  size: Tuple[int,int]=(BEAD,BEAD),
                  distance: int=1) -> Location:
    """Add a candidate location to the locations list."""
    orthogonal = directions[0:4]
    shuffle(orthogonal)
    diagonal = directions[4:8]
    shuffle(diagonal)
    shuffled = orthogonal + diagonal

    scaled = PVector.mult(shuffled[direction], distance)
    candidate_location = PVector.add(parent.coordinate, scaled)
    room_to_add = create_location(Room, candidate_location, locs, size)
    room_to_add.name = name
    locs.append(room_to_add)
    return room_to_add

def get_candidate_room(parents: List[Location], room_name: str,
                       locs: List[Location],
                       size: Tuple[int,int]=(BEAD,BEAD),
                       distance: int=1) -> Location | None:
    """Evaluate potental candidate Locations and return first viable."""
    for parent in parents:
        attempt = 0
        while attempt < 8:
            candidate = add_candidate(room_name, parent, attempt, locs, size, distance)

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

                for index,room in enumerate(rooms):
                    if distances[index] <= dist_to_parent:
                        room.add_neighbor(candidate)

                return candidate

            for room in rooms:
                if candidate in room.neighbors:
                    room.remove_neighbor(candidate)
            locs.remove(candidate)

            attempt += 1
        print("Next parent")

    print("No viable locations found!")
    return None

# start with priority-sorted list of parent locations
# take the first one
#   test candidate locations attached to parent for viability
#   bail out after some number of attempts?
# try another if none found
# how do we handle if _no_ viable locations can be found?
#
# might be better to sort the list by neighbor count rather than
# prune - sometimes the current approach can get stuck. It returns a
# very short list of parents, none of which have viable build locations
# adjacent.
def get_parent_rooms(types: List[str], mine_start: Location) -> List[Location]:
    """Return the parent room to attach a new room to."""
    parents = []
    for room_name in types:
        parents += mine_start.get_locations_by_name(room_name)

    neighbor_counts = [len(r.neighbors) for r in parents]
    if neighbor_counts:
        min_neighbors = min(neighbor_counts)
        return [r for r in parents if len(r.neighbors) == min_neighbors]

    return []

def dwarf_mine_factory(x_location: int, depth: int,
                       target_mineral: GoldVein | Mithril,
                       locs: List[Location]) -> List[Room]:
    """Generate the start of a Dwarf mine."""
    sites = []

    room0 = create_location(Room, PVector(x_location, GROUND_LEVEL), locs)
    room0.name = "Start"
    room0.color = DWARF
    sites.append(room0)

    half_height = (depth - GROUND_LEVEL)//2 + GROUND_LEVEL
    room1 = create_location(Room, PVector(x_location, half_height), locs)
    room1.name = "Barracks"
    room1.color = DWARF
    room1.contents = Entity("Dwarves", room1, CREATURE)
    sites.append(room1)

    room2 = create_location(Room, PVector(x_location, depth), locs)
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

def get_mine_start_location(target_mineral: Mithril | GoldVein) -> Tuple[int, int]:
    """Determine where to start the dwarf mine.

    Returns a tuple of (x_location, depth).
    """
    x_location = depth = 0
    if isinstance(target_mineral, Mithril):
        x_location = target_mineral.center.x
        depth = target_mineral.center.y

    if isinstance(target_mineral, GoldVein):
        if target_mineral.left.y < target_mineral.right.y:
            x_location = FINGER
            depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)
        elif target_mineral.right.y < target_mineral.left.y:
            # TO_DO: for testing
            #x_location = WIDTH - FINGER
            x_location = FINGER
            depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)
        else:
            if randint(0,1) == 9:
                x_location = FINGER
                depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)
            else:
                # TO_DO: for testing
                #x_location = WIDTH - FINGER
                x_location = FINGER
                depth = get_y_at_x(target_mineral.left, target_mineral.right, x_location)

    return (x_location, depth)

class MineStartStrategy(LocationStrategy):
    """Build the starting main shaft of a dwarven mine."""

    def __init__(self) -> None:
        """Create an instance of a MineStartStrategy object."""
        super().__init__()
        self.step = 1
        self.previous_node = None
        self.x_location = -1
        self.depth = -1
        self.target_mineral = None

    def __repr__(self) -> str:
        """Return the developer string representation of a MineStartStrategy."""
        return "MineStartStrategy()"

    def next(self, locs: List[Location]) -> Room:
        """Return the next location in the sequence."""
        result = None

        if not self.target_mineral:
            # pick a spot on the surface above a gold vein or mithril deposit
            minerals = [l for l in locs if isinstance(l, (Mithril, GoldVein))]
            self.target_mineral = choice(minerals)
            self.x_location, self.depth = get_mine_start_location(self.target_mineral)

        if self.step == 1:
            self.previous_node = create_location(Room, 
                                                 PVector(self.x_location, GROUND_LEVEL), 
                                                 locs)
            self.previous_node.name = "Start"
            self.previous_node.color = DWARF
            result = self.previous_node

        if self.step == 2:
            half_height = (self.depth - GROUND_LEVEL)//2 + GROUND_LEVEL
            room = create_location(Room, PVector(self.x_location, half_height), locs)
            room.name = "Barracks"
            room.color = DWARF
            room.contents = Entity("Dwarves", room, CREATURE)
            self.previous_node.add_neighbor(room)
            self.previous_node = room
            result = room

        if self.step == 3:
            self.done = True

            room = create_location(Room, PVector(self.x_location, self.depth), locs)
            room.name = "Mine"
            room.color = DWARF
            room.target = self.target_mineral
            room.contents = Entity("Treasure", room, TREASURE)
            self.previous_node.add_neighbor(room)
            result = room

        self.step += 1
        return result


class SpringStrategy(LocationStrategy):
    """Gather treasures and grow the population."""

    def __init__(self, mine_start: Room) -> None:
        """Create an instance of a SpringStrategy object."""
        super().__init__()
        self.mine_start = mine_start
        self.step = 1
        self.treasures = self.mine_start.get_all_matching_entities("Treasure")

    def __repr__(self) -> str:
        """Return the developer string representation of a SpringStrategy."""
        return "SpringStrategy()"

    # TO_DO: some ambiguity in the rules here - we want to gather all
    #        treasures from the mines and store them, but the rules do
    #        _not_ later say to make these 'Dwarven Treasures'. It is
    #        implied later that these small treasure rooms contain
    #        'regular' treasures, not 'Dwarven Treasures.' But if we
    #        don't distinguish them, we'll have an infinite loop of
    #        treasure room creation. Perhaps a new name for these?
    #        Alternatively, we can remove treasures at the end of the
    #        Age by room name, which is how the rules are written...
    def next(self, locs: List[Location]) -> Room | None:
        """Return the next location in the sequence."""
        result = None
        print("Calling SpringStrategy.next() -------------------------")

        if self.treasures:
            match self.step:
                case 1:
                    print("Adding Treasure Vault")

                    current_barracks = get_parent_rooms(["Barracks"], self.mine_start)
                    result = get_candidate_room(current_barracks, "Treasure Vault", locs)

                    if result:
                        result.contents = Entity("Dwarven Treasure", result, TREASURE)
                        check_for_connections(result, locs)

                    self.step += 1

                case 2:
                    print("Adding Barracks")
                    selection = get_parent_rooms(["Barracks", "Treasure Vault", "Outpost"],
                                                 self.mine_start)
                    result = get_candidate_room(selection, "Barracks", locs)

                    if result:
                        result.contents = Entity("Dwarves", result, CREATURE)
                        check_for_connections(result, locs)

                    self.step -= 1
                    source_treasure = self.treasures.pop()
                    source_treasure.parent.contents = None
                    source_treasure.detach()

        else:
            self.done = True

        return result


class SummerStrategy(LocationStrategy):
    """Dig new mines."""

    def __init__(self, mine_start: Room) -> None:
        """Create an instance of a SummerStrategy object."""
        super().__init__()
        self.mine_start = mine_start


# Age of Civilization
# TO_DO: implementing Dwarves first, Dark Elves to come later
class CivilizationAge():
    """Manages creation of the landscape and entities during the Age of Civilization."""

    def __init__(self) -> None:
        """Create an instance of a CivilizationAge object."""
        self.done = False
        self.step = 0
        self.mine_start = None
        self.year = 0
        self.name = "Age of Civilization"
        self.current_strategy = None

    # TO_DO: we will shift away from a list of new_locations
    #        to just one at a time
    def update(self, locs: List[Location]) -> List:
        """Return the next generated map location."""
        print("CivilizationAge.update()")
        new_locations = []

        # TO_DO: use GoldVeinStrategy here
        if not any(isinstance(l, (Mithril, GoldVein)) for l in locs):
            print("Adding gold vein")
            new_locations.append(GoldVein())
            return new_locations

        population = 0
        if self.step > 0:
            population = len(self.mine_start.get_all_matching_entities("Dwarves"))
        print(f"Population = {population}")

        if not self.mine_start:
            self.current_strategy = MineStartStrategy()

        # possible algorithm for handling steps:
        # 0. start with just the setup strategy in the queue
        # 1. pop off the queue
        # 2. execute next()
        # 3. if not done, go to 2
        # 4. if done, add next strategy to queue (if Age is not done)
        # 5. go to 1

        # is a queue warranted? seems like we'll only ever have one
        # active Strategy at a time - so maybe just a single 'current_builder'
        # pointer? the sequencing is happening _inside_ the strategies
        #
        # if we broke them up even finer, then maybe we would want to
        # accumulate a queue at this level, something to think about

        # the strategy approach could eliminate the need for a 'step'
        # counter and the match case structure below. What if the
        # strategy returned its successor when done?

        match self.step:
            case 0:
                print("Setup")
                new_locations.append(self.current_strategy.next(locs))

                # TO_DO: we can probably rework this awkward logic with the
                #        new approach... TBD
                if not self.mine_start:
                    self.mine_start = [r for r in new_locations if r.name == "Start"]
                    if self.mine_start:
                        self.mine_start = self.mine_start[0]

                if self.current_strategy.is_done():
                    self.step += 1
                    self.current_strategy = SpringStrategy(self.mine_start)

                return new_locations

            case 1:
                print(f"Year {self.year} Spring - gathering and growing")
                addition = self.current_strategy.next(locs)
                if addition:
                    print(f"Adding {addition}")
                    # TO_DO: Spring uses get_candidate_room(), which modifies locs list
                    #        may want to rethink this...
                    #new_locations.append(addition)

                if self.current_strategy.is_done():
                    self.step += 1
                    # TO_DO: temporary loop-back util Summer has been implemented
                    self.current_strategy = SpringStrategy(self.mine_start)
                    #self.current_strategy = SummerStrategy(self.mine_start)

                return new_locations

            case 2:
                print(f"Year {self.year} Summer - digging new mines")
                # TO_DO: should restrict to mines connected to this start
                #        (though admittedly I don't think we can have more
                #        than one at this point, so perhaps moot?)
                mines = [l for l in locs if l.name == "Mine"]

                # we want to add mines at the ends of a GoldVein, or
                # at the points of a Mithril deposit
                x_coords = [m.coordinate.x for m in mines]
                mine_max_x = max(x_coords)
                mine_min_x = min(x_coords)

                endpoints = []
                if mine_max_x < WIDTH - ROOM_SPACING - BEAD:
                    endpoints.append(mine_max_x)

                if mine_min_x > ROOM_SPACING + BEAD:
                    endpoints.append(mine_min_x)

                potential_parents = [m for m in mines if m.coordinate.x in endpoints]
                parent_mine = choice(potential_parents)

                direction = 1
                if parent_mine.coordinate.x == mine_min_x:
                    direction = -1

                deposit = parent_mine.target

                # TO_DO: we need the same tests for collision as in
                #        get_candidate_room()
                if isinstance(deposit, GoldVein):
                    new_x = parent_mine.coordinate.x + (direction * ROOM_SPACING)
                    new_y = get_y_at_x(deposit.left, deposit.right, new_x)
                    new_room = create_location(Room, PVector(new_x, new_y), locs)
                    new_room.name = "Mine"
                    new_room.target = parent_mine.target
                    new_room.color = parent_mine.color
                    parent_mine.add_neighbor(new_room)
                    new_room.contents = Entity("Treasure", new_room, TREASURE)
                    new_locations.append(new_room)

                if isinstance(deposit, Mithril):
                    # TO_DO: only works when the mine is centered on the deposit
                    #        need a better approach here
                    to_corner = PVector.mult(deposit.corner_vector, ROOM_SPACING)
                    new_location = PVector.sub(parent_mine.coordinate, to_corner)
                    new_room = create_location(Room, new_location, locs)
                    new_room.name = "Mine"
                    new_room.target = parent_mine.target
                    new_room.color = parent_mine.color
                    parent_mine.add_neighbor(new_room)
                    new_room.contents = Entity("Treasure", new_room, TREASURE)
                    new_locations.append(new_room)

                self.step += 1
                return new_locations

            case 3:
                print(f"Year {self.year} Autumn - building")
                all_rooms = self.mine_start.get_all_connected_locations()

                match population:
                    case 3:
                        # TO_DO: vary the size & shape of workshops
                        print("Workshops")
                        selection = choice(get_parent_rooms(["Mine"], self.mine_start))
                        new_location = PVector(selection.coordinate.x,
                                               selection.coordinate.y + ROOM_SPACING)
                        new_room = create_location(Room, new_location, locs, (BEAD*2,BEAD))
                        new_room.name = "Workshop"
                        new_room.color = selection.color
                        selection.add_neighbor(new_room)
                        new_locations.append(new_room)

                    case 4:
                        print("Great Hall")
                        selection = get_parent_rooms(["Barracks", "Treasure Vault"],
                                                     self.mine_start)

                        # TO_DO: need to customize size/shape of Great Hall
                        new_room = get_candidate_room(selection, "Great Hall", locs,
                                                      (FINGER//2, BEAD))

                        if new_room:
                            new_room.contents = Entity("Dwarven Treasure", new_room, TREASURE)
                            check_for_connections(new_room, locs)

                    case 5:
                        print("Exploratory Shaft")
                        shaft_x = self.mine_start.coordinate.x
                        shaft_rooms = [m for m in all_rooms if m.coordinate.x == shaft_x]
                        shaft_rooms.sort(key=lambda room: room.coordinate.y)
                        shaft_bottom = shaft_rooms.pop()

                        new_location = PVector(shaft_bottom.coordinate.x,
                                               shaft_bottom.coordinate.y + FINGER)
                        new_room = create_location(Room, new_location, locs)
                        new_room.name = "Outpost"
                        new_room.color = shaft_bottom.color
                        shaft_bottom.add_neighbor(new_room)
                        new_locations.append(new_room)

                        if new_room.coordinate.y > HEIGHT:
                            self.done = True

                    case 6:
                        print("Hall Expansion")
                        candidates = self.mine_start.get_locations_by_name("Great Hall")
                        if candidates:
                            great_hall = candidates[0]
                            new_x = great_hall.rect.x - BEAD
                            new_w = great_hall.rect.w + (BEAD * 2)
                            great_hall.rect = Rect(new_x,
                                                   great_hall.rect.y,
                                                   new_w,
                                                   great_hall.rect.h)

                    case 7:
                        print("Hall of Records")
                        selection = get_parent_rooms(["Great Hall"], self.mine_start)
                        new_room = None
                        if selection:
                            new_room = get_candidate_room(selection, "Hall of Records", locs,
                                                          (BEAD, BEAD), 3)

                        if new_room:
                            new_room.contents = Entity("Dwarven Treasure", new_room, TREASURE)
                            check_for_connections(new_room, locs)

                    # TO_DO: name the city
                    case 8:
                        print("Dwarven Golden Age City")
                        selection = get_parent_rooms(["Barracks", "Treasure Vault"],
                                                     self.mine_start)
                        new_room = get_candidate_room(selection, "Dwarven City", locs,
                                                      (FINGER, BEAD))

                        if new_room:
                            new_room.contents = Entity("Dwarven Treasure", new_room, TREASURE)
                            check_for_connections(new_room, locs)

                    # TO_DO: Treasure Room should not connect to rest of dwarf mine
                    case 9:
                        print("Treasure Room")
                        new_room = get_candidate_room(all_rooms, "Treasure Room", locs,
                                                      (BEAD*2, BEAD*2),
                                                      ROOM_SPACING * 3)

                        if new_room:
                            treasure = Entity("Dwarven Treasure", new_room, TREASURE)
                            treasure.value = 2
                            new_room.contents = treasure

                    # TO_DO: cook up a better approach, we could still run off the
                    #        end of this and get stuck, in theory
                    case 10 | 11 | 12 | 13 | 14 | 15:
                        print("Delve Too Deep")
                        self.done = True

                        # might be simpler to sort by y coordinate and pop...
                        y_coords = [m.coordinate.y for m in all_rooms]
                        mine_max_y = max(y_coords)

                        potential_bottom = [m for m in all_rooms if m.coordinate.y == mine_max_y]
                        bottom = choice(potential_bottom)

                        shaft_x = bottom.coordinate.x
                        shaft_y = HEIGHT + BEAD

                        new_room = create_location(Room, PVector(shaft_x, shaft_y), locs)
                        new_room.name = "End"
                        new_room.color = bottom.color
                        bottom.add_neighbor(new_room)
                        new_locations.append(new_room)

                self.step += 1
                return new_locations

            # TO_DO: haven't implemented conflict or death yet - need to track and
            #        build tombs accordingly once we do...
            case 4:
                print(f"Year {self.year} Winter - mourning")

                self.step = 1
                self.year += 1
                return new_locations

        return new_locations

    def is_done(self) -> bool:
        """Return whether the CivilizationAge has completed or not."""
        return self.done
