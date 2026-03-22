"""Contains Entity class to represent room & cavern contents."""
from random import choice
from typing import Tuple
from engine import screen
from pvector import PVector
from location import Location
from constants import BEAD, TREASURE, EVENT, DWARF, BEASTS, WYRM


# TO_DO: moving to a hierarchy - this one should become an ABC
class Entity():
    """Represents creatures and things on the map."""

    def __init__(self, name: str, parent: Location, color: Tuple=(128,128,128)) -> None:
        """Create an instance of an entity."""
        self.name = name
        self._parent = parent

        # pylint: disable=C0103
        # C0103: Attribute name doesn't conform to snake_case naming style (invalid-name)
        self.x = self.parent.coordinate.x
        self.y = self.parent.coordinate.y

        self.radius = BEAD//3
        self.color = color
        self.value = 1

        self.is_dead = False

    def __str__(self) -> str:
        """Return the string representation of an Entity."""
        return self.name

    def __repr__(self) -> str:
        """Return the developer string representation of an Entity."""
        return f"{self.name} ({self.parent})"

    @property
    def parent(self) -> Location:
        """Return the Entity's parent Location."""
        return self._parent

    @parent.setter
    def parent(self, new_parent: Location) -> None:
        """Set the Entity's parent Location."""
        new_parent.contents = self
        self._parent = new_parent

        if not self.destination:
            self.x = self.parent.coordinate.x
            self.y = self.parent.coordinate.y

    def detach(self) -> None:
        """Detach the Entity from its parent without setting a new one."""
        self._parent.contents = None
        self._parent = None

    def move(self, destination: Location) -> None:
        """Move the Entity to a new Location."""

    def update(self) -> None:
        """Update the Entity's state once per frame."""

    def draw(self) -> None:
        """Draw the Entity on the screen once per frame."""
        screen.draw.circle(self.x, self.y, self.radius, self.color, 0)
        screen.draw.text(f"{self.value}", center=(self.x, self.y))

        if self.is_dead:
            screen.draw.text("X", center=(self.x, self.y), color=Color('red'))

    def think(self) -> None:
        """Decide what action to take and queue it up once per game tick."""

        # Timing is a question here once we start animating
        # need to complete all animations between game ticks
        # and interactions between Entities need to consider this too
        # for example, an attack should be resolved immediately so
        # that the target can't choose to move away or any other
        # interruption

        # Concern that the game logic works against room occupancy,
        # not actual screen coordinates - but again, the animation is
        # just sugar over the game state. As long as the animation
        # finishes before the next tick we should be OK.

        # Another issue I'm already seeing with just move() implemented:
        # two creatures can choose the same destination and after the
        # move, one of them disappears (is probably an invisible zombie)
        # we should lay claim to the destination immediately as well -
        # so same principal as attack: the _effect_ of an action
        # takes place immediately, since the entities are acting in
        # serial order. But the on-screen visible 'effect' can
        # take as much time as desired before the next tick.


class Creature(Entity):
    """Represents creatures on the map."""

    def __init__(self, name: str, parent: Location) -> None:
        """Create an instance of a Creature object."""
        super().__init__(name, parent, (128,128,128))

        # TO_DO: probably going to end up with subclasses,
        #        but go with just colors for now until
        #        behavior starts to fragment
        if self.name == "Dwarves":
            self.color = DWARF
        if self.name == "Primordial Beasts":
            self.color = BEASTS
        if self.name == "Ancient Wyrm":
            self.color = WYRM

        self.destination = None
        self.velocity = None

    def move(self, destination: Location) -> None:
        """Move the Creature to a new Location."""
        self.destination = destination

        vector = PVector.sub(self.destination.coordinate, self.parent.coordinate)
        vector / 50    # arrive in 50 frames
        self.velocity = vector

        self.detach()
        self.parent = self.destination

    def think(self) -> None:
        """Decide what action to take and queue it up once per game tick."""
        nearby = self.parent.neighbors
        neighbors = [l.contents for l in nearby if l.contents]

        vacancies = [l for l in nearby if not l.contents]
        if vacancies:
            target = choice(vacancies)
            self.move(target)

    def update(self) -> None:
        """Update the Creature's state once per frame."""
        if self.velocity:
            self.x += self.velocity.x
            self.y += self.velocity.y

        if self.destination:
            EPSILON = 0.01
            min_x = self.destination.coordinate.x - EPSILON
            max_x = self.destination.coordinate.x + EPSILON
            min_y = self.destination.coordinate.y - EPSILON
            max_y = self.destination.coordinate.y + EPSILON
            if min_x <= self.x <= max_x and min_y <= self.y <= max_y:

                self.velocity = None
                self.destination = None


class Treasure(Entity):
    """Represents treasure on the map."""

    def __init__(self, name: str, parent: Location) -> None:
        """Create an instance of a Treasure object."""
        super().__init__(name, parent, TREASURE)


class Event(Entity):
    """Represents events on the map."""

    def __init__(self, name: str, parent: Location) -> None:
        """Create an instance of an Event object."""
        super().__init__(name, parent, EVENT)
