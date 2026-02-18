"""Contains Entity class to represent room & cavern contents."""
from typing import Tuple
from engine import screen
from location import Location
from constants import BEAD


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
        self._parent = new_parent
        self.x = self.parent.coordinate.x
        self.y = self.parent.coordinate.y

    def draw(self) -> None:
        """Draw the Entity on the screen once per frame."""
        screen.draw.circle(self.x, self.y, self.radius, self.color, 0)
