"""Contains the PrimordialAge class and supporting functions."""
import math
from random import randint
from typing import List
from pvector import PVector
from constants import CAVERN, CREATURE, BEAD, FINGER, EVENT, TREASURE
from entity import Entity
from landscape import GoldVein, UndergroundRiver, get_random_underground_location
from location import Cavern, Location
from utilities import create_location, out_of_bounds

class LocationStrategy:
    """Base class for LocationStrategy builders."""

    def __init__(self) -> None:
        """Create an instance of a LocationStrategy object."""
        self.done = False

    def next(self) -> List:
        """Return the next location in the sequence."""
        self.done = True    # TO_DO: temporary to make stubs work
        return []

    def is_done(self) -> bool:
        """Return whether the LocationStrategy is complete or not."""
        return self.done

# TO_DO: strategy.next() should return individual locations
#        not a list

class GoldVeinStrategy(LocationStrategy):
    """Build a GoldVein."""

    def __repr__(self) -> str:
        """Return the developer string representation of a GoldVeinStrategy."""
        return "GoldVeinStrategy()"

    def next(self) -> List:
        """Return the next location in the sequence."""
        self.done = True
        return [GoldVein()]

class MithrilStrategy(LocationStrategy):
    """Build a Mithril deposit."""

    def __repr__(self) -> str:
        """Return the developer string representation of a MithrilStrategy."""
        return "MithrilStrategy()"

class SimpleCavernStrategy(LocationStrategy):
    """Build a random number of simple Caverns."""

    def __repr__(self) -> str:
        """Return the developer string representation of a SimpleCavernStrategy."""
        return "SimpleCavernStrategy()"

class ComplexCavernStrategy(LocationStrategy):
    """Build a complex Cavern."""

    def __repr__(self) -> str:
        """Return the developer string representation of a ComplexCavernStrategy."""
        return "ComplexCavernStrategy()"

class UndergroundRiverStrategy(LocationStrategy):
    """Build an UndergroundRiver."""

    def __repr__(self) -> str:
        """Return the developer string representation of a UndergroundRiverStrategy."""
        return "UndergroundRiverStrategy()"

class AncientWyrmStrategy(LocationStrategy):
    """Build an AncientWyrm lair."""

    def __repr__(self) -> str:
        """Return the developer string representation of a AncientWyrmStrategy."""
        return "AncientWyrmStrategy()"

def natural_cavern_factory(locs: List[Location]) -> Cavern:
    """Generate a natural cavern."""
    coordinate = get_random_underground_location()

    cavern = create_location(Cavern, coordinate, locs)
    cavern.color = CAVERN

    detail = randint(1,6)
    match detail:
        case 1:
            cavern.tunnel = True
            cavern.tilt = randint(-FINGER//2, FINGER//2)
        case 2:
            event = Entity("Plague", cavern, EVENT)
            event.value = randint(1,4)
            cavern.contents = event
        case 3:
            treasure = Entity("Gemstones", cavern, TREASURE)
            treasure.value = randint(1,4)
            cavern.contents = treasure
        case 4:
            pass
        case 5:
            cavern.contents = Entity("Primordial Beasts", cavern, CREATURE)
        case 6:
            cavern.contents = Entity("Fate", cavern, EVENT)

    return cavern

def add_caverns(locs: List[Location]) -> List[Location]:
    """Generate a random number of Caverns."""
    new_locations = [natural_cavern_factory(locs)]
    cavern_count = 1
    while randint(1,6) < 6 and cavern_count < 6:
        new_locations.append(natural_cavern_factory(locs))
        cavern_count += 1
    return new_locations

def get_orbital_point(origin: PVector, radius: int, angle: int) -> PVector:
    """Generate a point on a circle of given radius and angle around an origin."""
    new_x = new_y = -1
    while out_of_bounds(PVector(new_x, new_y)):
        new_x = radius * math.cos(math.radians(angle)) + origin.x
        new_y = radius * math.sin(math.radians(angle)) + origin.y
    return PVector(new_x, new_y)

def cave_complex_factory(locs: List[Location]) -> List[Cavern]:
    """Generate a cave complex."""
    radius = BEAD
    sites = []

    first_point = get_random_underground_location()
    cavern1 = create_location(Cavern, first_point, locs)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Primordial Beasts", cavern1, CREATURE)
    sites.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, 3 * radius, angle_1)
    cavern2 = create_location(Cavern, second_point, locs)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Primordial Beasts", cavern2, CREATURE)
    sites.append(cavern2)

    angle_2 = angle_1 + randint(70,290)
    third_point = get_orbital_point(first_point, 3 * radius, angle_2)
    cavern3 = create_location(Cavern, third_point, locs)
    cavern3.color = CAVERN
    cavern3.contents = Entity("Primordial Beasts", cavern3, CREATURE)
    sites.append(cavern3)

    sites[0].add_neighbor(sites[1])
    sites[0].add_neighbor(sites[2])

    return sites

# TO_DO: name the wyrm
def ancient_wyrm_factory(locs: List[Location]) -> List[Cavern]:
    """Generate a cavern containing an ancient wyrm."""
    radius = BEAD
    sites = []

    first_point = get_random_underground_location()
    cavern1 = create_location(Cavern, first_point, locs)
    cavern1.color = CAVERN
    cavern1.contents = Entity("Ancient Wyrm", cavern1, CREATURE)
    sites.append(cavern1)

    angle_1 = randint(0,359)
    second_point = get_orbital_point(first_point, radius * 1.5, angle_1)
    cavern2 = create_location(Cavern, second_point, locs)
    cavern2.color = CAVERN
    cavern2.contents = Entity("Wyrm Treasure", cavern2, TREASURE)
    sites.append(cavern2)

    sites[0].add_neighbor(sites[1])

    return sites


class PrimordialAge():
    """Manages creation of the landscape and entities during the Primordial Age."""

    def __init__(self) -> None:
        """Create an instance of a PrimordialAge object."""
        self.name = "Primordial Age"
        self.done = False

        self.builders = []

        for _ in range(3):
            check = randint(0,6)
            match check:
                case 0:
                    # TO_DO: for testing
                    #self.builders.append(MithrilStrategy())
                    self.builders.append(GoldVeinStrategy())
                case 1 | 2:
                    self.builders.append(SimpleCavernStrategy())
                case 3:
                    self.builders.append(GoldVeinStrategy())
                case 4:
                    self.builders.append(ComplexCavernStrategy())
                case 5:
                    self.builders.append(UndergroundRiverStrategy())
                case 6:
                    self.builders.append(AncientWyrmStrategy())
            # TO_DO: there is an additional choice for natural disasters,
            #        implement when we come to that rule

        self.current_builder = self.builders.pop(0)

    def update(self, locs: List[Location]) -> List:
        """Return the next generated map location."""
        print("PrimordialAge.update()")

        # TO_DO: this model is shifting to one location at a time,
        #        so we'll be doing away with this list
        new_locations = []

        if self.current_builder.is_done():
            if self.builders:
                self.current_builder = self.builders.pop(0)
            else:
                self.done = True
                return []

        new_locations += self.current_builder.next()

        print(self.builders)
        print(self.current_builder)

        #check = randint(0,6)
        #match check:
            #case 0:
                ## TO_DO: for testing
                ##new_locations.append(Mithril())
                #new_locations.append(GoldVein())
            #case 1 | 2:
                #new_locations += add_caverns(locs)
            #case 3:
                #new_locations.append(GoldVein())
            #case 4:
                #new_locations += cave_complex_factory(locs)
            #case 5:
                #river = UndergroundRiver()
                #new_locations.append(river)
                #for coord in river.caves:
                    #new_cavern = create_location(Cavern, coord, locs)
                    #new_cavern.color = CAVERN
                    #new_locations.append(new_cavern)
            #case 6:
                #new_locations += ancient_wyrm_factory(locs)

        return new_locations

    def is_done(self) -> bool:
        """Return whether the PrimordialAge has completed or not."""
        return self.done
