"""Contains the PrimordialAge class and supporting functions."""
import math
from random import randint
from typing import List, Any
from pvector import PVector
from constants import CAVERN, BEAD, FINGER
from entity import Creature, Treasure, Event
from landscape import GoldVein, UndergroundRiver, get_random_underground_location, Mithril
from location import Cavern, Location
from location_strategy import LocationStrategy
from utilities import create_location, out_of_bounds

def get_orbital_point(origin: PVector, radius: int, 
                      min_angle: int, max_angle: int) -> PVector:
    """Generate a point on a circle of given radius and angle around an origin."""
    new_x = new_y = -1
    while out_of_bounds(PVector(new_x, new_y)):
        angle = randint(min_angle, max_angle)
        new_x = radius * math.cos(math.radians(angle)) + origin.x
        new_y = radius * math.sin(math.radians(angle)) + origin.y
    return PVector(new_x, new_y)


class GoldVeinStrategy(LocationStrategy):
    """Build a GoldVein."""

    def __repr__(self) -> str:
        """Return the developer string representation of a GoldVeinStrategy."""
        return "GoldVeinStrategy()"

    def next(self, locs: List[Location]) -> GoldVein:
        """Return the next location in the sequence."""
        self.done = True
        return GoldVein()


class MithrilStrategy(LocationStrategy):
    """Build a Mithril deposit."""

    def __repr__(self) -> str:
        """Return the developer string representation of a MithrilStrategy."""
        return "MithrilStrategy()"

    def next(self, locs: List[Location]) -> Mithril:
        """Return the next location in the sequence."""
        self.done = True
        return Mithril()


class SimpleCavernStrategy(LocationStrategy):
    """Build a random number of simple Caverns."""

    def __init__(self) -> None:
        """Create an instance of a SimpleCavernStrategy object."""
        super().__init__()
        self.cavern_count = 0

    def __repr__(self) -> str:
        """Return the developer string representation of a SimpleCavernStrategy."""
        return "SimpleCavernStrategy()"

    def next(self, locs: List[Location]) -> Cavern:
        """Return the next location in the sequence."""
        self.cavern_count += 1
        if randint(1,6) == 6 or self.cavern_count >= 6:
            self.done = True
        return self._natural_cavern_factory()

    def _natural_cavern_factory(self) -> Cavern:
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
                event = Event("Plague", cavern)
                event.value = randint(1,4)
                cavern.contents = event
            case 3:
                treasure = Treasure("Gemstones", cavern)
                treasure.value = randint(1,4)
                cavern.contents = treasure
            case 4:
                pass
            case 5:
                cavern.contents = Creature("Primordial Beasts", cavern)
            case 6:
                cavern.contents = Event("Fate", cavern)

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

    # TO_DO: remove locs parameter
    def next(self, locs: List[Location]) -> Cavern:
        """Return the next location in the sequence."""
        result = None

        if self.step == 1:
            point = get_random_underground_location()
            self.start_node = create_location(Cavern, point)
            self.start_node.color = CAVERN
            self.start_node.contents = Creature("Primordial Beasts", self.start_node)
            result = self.start_node

        if self.step == 2:
            point = get_orbital_point(self.start_node.coordinate, 
                                      self.radius * 3, 0, 359)
            cavern = create_location(Cavern, point)
            cavern.color = CAVERN
            cavern.contents = Creature("Primordial Beasts", cavern)
            self.start_node.add_neighbor(cavern)
            result = cavern

        if self.step == 3:
            self.done = True

            # TO_DO: rework this to use viability check instead of constrained angular offset
            point = get_orbital_point(self.start_node.coordinate, 
                                      self.radius * 3, 0, 359)
            cavern = create_location(Cavern, point)
            cavern.color = CAVERN
            cavern.contents = Creature("Primordial Beasts", cavern)
            self.start_node.add_neighbor(cavern)
            result = cavern

        self.step += 1
        return result


# TO_DO: due to the references to self.river, this probably doesn't get
#        cleaned up when it's done. We may want an explicit garbage collection
#        on finished LocationStrategies, or change how references are passed around.
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

    # TO_DO: remove locs parameter
    def next(self, locs: List[Location]) -> UndergroundRiver | Cavern:
        """Return the next location in the sequence."""
        result = None
        
        if self.step == 0:
            self.river = UndergroundRiver()
            self.total_steps = len(self.river.caves) + 1
            result = self.river
        else:
            cavern = create_location(Cavern, self.river.caves[self.step-1])
            cavern.color = CAVERN
            result = cavern

        self.step += 1

        if self.step >= self.total_steps:
            self.done = True

        return result


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
    # TO_DO: remove locs parameter
    def next(self, locs: List[Location]) -> Cavern:
        """Return the next location in the sequence."""
        result = None

        if self.step == 1:
            point = get_random_underground_location()
            self.start_node = create_location(Cavern, point)
            self.start_node.color = CAVERN
            self.start_node.contents = Creature("Ancient Wyrm", self.start_node)
            result = self.start_node

        if self.step == 2:
            self.done = True

            point = get_orbital_point(self.start_node.coordinate, 
                                      self.radius * 1.5, 0, 359)
            cavern = create_location(Cavern, point)
            cavern.color = CAVERN
            cavern.contents = Treasure("Wyrm Treasure", cavern)
            self.start_node.add_neighbor(cavern)
            result = cavern

        self.step += 1
        return result


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
                    #self.builders.append(MithrilStrategy())
                    # TO_DO: for testing
                    self.builders.append(GoldVeinStrategy())
                case 1 | 2:
                    self.builders.append(SimpleCavernStrategy())
                    # TO_DO: for testing
                    #self.builders.append(ComplexCavernStrategy())
                case 3:
                    self.builders.append(GoldVeinStrategy())
                    # TO_DO: for testing
                    #self.builders.append(ComplexCavernStrategy())
                case 4:
                    self.builders.append(ComplexCavernStrategy())
                case 5:
                    self.builders.append(UndergroundRiverStrategy())
                    # TO_DO: for testing
                    #self.builders.append(ComplexCavernStrategy())
                case 6:
                    self.builders.append(AncientWyrmStrategy())
                    # TO_DO: for testing
                    #self.builders.append(ComplexCavernStrategy())
            # TO_DO: there is an additional choice for natural disasters,
            #        implement when we come to that rule

        self.current_builder = self.builders.pop(0)

    def update(self, locs: List[Location]) -> List:
        """Return the next generated map location."""
        print("PrimordialAge.update()")

        #esult = None

        if self.current_builder.is_done():
            if self.builders:
                self.current_builder = self.builders.pop(0)
            else:
                self.done = True
                return []

        #result = self.current_builder.next(locs)

        print(self.builders)
        print(self.current_builder)

        # TO_DO: returning a list for compatibility, until
        #        all other Ages have been refactored to this model
        return [self.current_builder.next(locs)]

    def is_done(self) -> bool:
        """Return whether the PrimordialAge has completed or not."""
        return self.done
