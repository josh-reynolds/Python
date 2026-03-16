"""Contains the PrimordialAge class and supporting functions."""
import math
from random import randint
from typing import List
from pvector import PVector
from constants import CAVERN, CREATURE, BEAD, FINGER, EVENT, TREASURE
from entity import Entity
from landscape import GoldVein, UndergroundRiver, get_random_underground_location, Mithril
from location import Cavern, Location
from utilities import create_location, out_of_bounds

def get_orbital_point(origin: PVector, radius: int, angle: int) -> PVector:
    """Generate a point on a circle of given radius and angle around an origin."""
    new_x = new_y = -1
    while out_of_bounds(PVector(new_x, new_y)):
        new_x = radius * math.cos(math.radians(angle)) + origin.x
        new_y = radius * math.sin(math.radians(angle)) + origin.y
    return PVector(new_x, new_y)


class LocationStrategy:
    """Base class for LocationStrategy builders."""

    def __init__(self) -> None:
        """Create an instance of a LocationStrategy object."""
        self.done = False

    def next(self, locs: List[Location]) -> List:
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

    def next(self, locs: List[Location]) -> List:
        """Return the next location in the sequence."""
        self.done = True
        return [GoldVein()]


class MithrilStrategy(LocationStrategy):
    """Build a Mithril deposit."""

    def __repr__(self) -> str:
        """Return the developer string representation of a MithrilStrategy."""
        return "MithrilStrategy()"

    def next(self, locs: List[Location]) -> List:
        """Return the next location in the sequence."""
        self.done = True
        return [Mithril()]


class SimpleCavernStrategy(LocationStrategy):
    """Build a random number of simple Caverns."""

    def __init__(self) -> None:
        """Create an instance of a SimpleCavernStrategy object."""
        super().__init__()
        self.cavern_count = 0

    def __repr__(self) -> str:
        """Return the developer string representation of a SimpleCavernStrategy."""
        return "SimpleCavernStrategy()"

    def next(self, locs: List[Location]) -> List:
        """Return the next location in the sequence."""
        self.cavern_count += 1
        if randint(1,6) == 6 or self.cavern_count >= 6:
            self.done = True
        return [self._natural_cavern_factory(locs)]

    def _natural_cavern_factory(self, locs: List[Location]) -> Cavern:
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


class ComplexCavernStrategy(LocationStrategy):
    """Build a complex Cavern."""

    def __init__(self) -> None:
        """Create an instance of a ComplexCavernStrategy object."""
        super().__init__()
        self.step = 1
        self.radius = BEAD
        self.start_node = None
        self.previous_angle = 0

    def __repr__(self) -> str:
        """Return the developer string representation of a ComplexCavernStrategy."""
        return "ComplexCavernStrategy()"

    def next(self, locs: List[Location]) -> List:
        """Return the next location in the sequence."""
        sites = []

        if self.step == 1:
            point = get_random_underground_location()
            self.start_node = create_location(Cavern, point, locs)
            self.start_node.color = CAVERN
            self.start_node.contents = Entity("Primordial Beasts", self.start_node, CREATURE)
            sites.append(self.start_node)

        if self.step == 2:
            angle = randint(0,359)
            self.previous_angle = angle
            point = get_orbital_point(self.start_node.coordinate, self.radius * 3, angle)
            cavern = create_location(Cavern, point, locs)
            cavern.color = CAVERN
            cavern.contents = Entity("Primordial Beasts", cavern, CREATURE)
            self.start_node.add_neighbor(cavern)
            sites.append(cavern)

        if self.step == 3:
            self.done = True

            # TO_DO: rework this to use viability check instead of constrained angular offset
            angle = self.previous_angle + randint(70,290)
            point = get_orbital_point(self.start_node.coordinate, self.radius * 3, angle)
            cavern = create_location(Cavern, point, locs)
            cavern.color = CAVERN
            cavern.contents = Entity("Primordial Beasts", cavern, CREATURE)
            self.start_node.add_neighbor(cavern)
            sites.append(cavern)

        self.step += 1
        return sites


class UndergroundRiverStrategy(LocationStrategy):
    """Build an UndergroundRiver."""

    def __init__(self) -> None:
        """Create an instance of an UndergroundRiverStrategy object."""
        super().__init__()
        self.river = None
        self.step = 0
        self.total_steps = 1

    def __repr__(self) -> str:
        """Return the developer string representation of a UndergroundRiverStrategy."""
        return "UndergroundRiverStrategy()"

    def next(self, locs: List[Location]) -> List:
        """Return the next location in the sequence."""
        sites = []
        
        if self.step == 0:
            self.river = UndergroundRiver()
            self.total_steps = len(self.river.caves) + 1
            sites.append(self.river)
        else:
            cavern = create_location(Cavern, self.river.caves[self.step-1], locs)
            cavern.color = CAVERN
            sites.append(cavern)

        self.step += 1

        if self.step >= self.total_steps:
            self.done = True

        return sites


class AncientWyrmStrategy(LocationStrategy):
    """Build an AncientWyrm lair."""

    def __init__(self) -> None:
        """Create an instance of an AncientWyrmStrategy object."""
        super().__init__()
        self.step = 1
        self.radius = BEAD
        self.start_node = None

    def __repr__(self) -> str:
        """Return the developer string representation of a AncientWyrmStrategy."""
        return "AncientWyrmStrategy()"

    # TO_DO: name the wyrm
    def next(self, locs: List[Location]) -> List:
        """Return the next location in the sequence."""
        sites = []

        if self.step == 1:
            point = get_random_underground_location()
            self.start_node = create_location(Cavern, point, locs)
            self.start_node.color = CAVERN
            self.start_node.contents = Entity("Ancient Wyrm", self.start_node, CREATURE)
            sites.append(self.start_node)

        if self.step == 2:
            self.done = True

            angle = randint(0,359)
            point = get_orbital_point(self.start_node.coordinate, self.radius * 1.5, angle)
            cavern = create_location(Cavern, point, locs)
            cavern.color = CAVERN
            cavern.contents = Entity("Wyrm Treasure", cavern, TREASURE)
            self.start_node.add_neighbor(cavern)
            sites.append(cavern)

        self.step += 1
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
                    self.builders.append(MithrilStrategy())
                    # TO_DO: for testing
                    #self.builders.append(GoldVeinStrategy())
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

        new_locations += self.current_builder.next(locs)

        print(self.builders)
        print(self.current_builder)


        return new_locations

    def is_done(self) -> bool:
        """Return whether the PrimordialAge has completed or not."""
        return self.done
