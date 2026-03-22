"""Contains Entity class to represent room & cavern contents."""
from random import choice
from typing import Tuple
from engine import screen
from location import Location
from constants import BEAD, CREATURE, TREASURE, EVENT


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
        self.x = self.parent.coordinate.x
        self.y = self.parent.coordinate.y

    def detach(self) -> None:
        """Detach the Entity from its parent without setting a new one."""
        self._parent.contents = None
        self._parent = None

    # TO_DO: Would be nice to animate this movement rather than
    #        all in one big jump. Will need to consider timers and
    #        relationship between frames and game ticks.
    def move(self, destination: Location) -> None:
        """Move the Entity to a new Location."""
        self.detach()
        self.parent = destination

    def draw(self) -> None:
        """Draw the Entity on the screen once per frame."""
        screen.draw.circle(self.x, self.y, self.radius, self.color, 0)
        screen.draw.text(f"{self.value}", center=(self.x, self.y))

        if self.is_dead:
            screen.draw.text("X", center=(self.x, self.y), color=Color('red'))

    def think(self) -> None:
        """Decide what action to take and queue it up once per game tick."""
        nearby = self.parent.neighbors
        neighbors = [l.contents for l in nearby if l.contents]

        #print(f"{self} : {nearby} : {neighbors}")

        if self.color == CREATURE:
            vacancies = [l for l in nearby if not l.contents]
            if vacancies:
                target = choice(vacancies)
                self.move(target)


class Creature(Entity):
    """Represents creatures on the map."""

    def __init__(self, name: str, parent: Location) -> None:
        """Create an instance of a Creature object."""
        super().__init__(name, parent, CREATURE)


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
