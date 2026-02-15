"""Contains Entity class to represent room & cavern contents."""
from typing import Tuple
from engine import screen
from location import Location

BEAD = 30       # duplicated from main

class Entity():
    def __init__(self, name: str, parent: Location, color: Tuple=(128,128,128)) -> None:
        self.name = name
        self._parent = parent
        self.x = self.parent.coordinate.x
        self.y = self.parent.coordinate.y
        self.radius = BEAD//3
        self.color = color

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.name} ({self.parent})"

    @property
    def parent(self) -> Location:
        return self._parent

    @parent.setter
    def parent(self, new_parent: Location) -> None:
        self._parent = new_parent
        self.x = self.parent.coordinate.x
        self.y = self.parent.coordinate.y

    def draw(self) -> None:
        screen.draw.circle(self.x, self.y, self.radius, self.color, 0)
