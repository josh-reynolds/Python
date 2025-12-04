"""Contains the Baggage class and a factory function.

Baggage - represents passenger baggage.
baggage_from() - creates a Baggage object from a parsed source string.
"""
from typing import Mapping
from src.coordinate import Coordinate
from src.freight import Freight
from src.star_system import StarSystem, Hex, verify_world

class Baggage(Freight):
    """Represents passenger baggage."""

    def __init__(self, source_world: StarSystem,
                 destination_world: StarSystem) -> None:
        """Create an instance of Baggage."""
        super().__init__(1, source_world, destination_world)
        self.name = "Baggage"

    def __repr__(self) -> str:
        """Return the string representation of a piece of Baggage."""
        return f"Baggage({self.source_world!r}, {self.destination_world!r})"

    def encode(self) -> str:
        """Return a string encoding the Baggage object to save and load state."""
        return f"Baggage - {self.source_world.coordinate} - {self.destination_world.coordinate}"


def baggage_from(source: str, destination: str,
                 systems: Mapping[Coordinate, Hex]) -> Baggage:
    """Create a Baggage object from a parsed source string.

    Both coordinate arguments are in the format : (d,d,d), all +/- integers.

    The function also needs access to a dictionary of StarSystems, and
    the coordinates must be keys in that dictionary.
    """
    source_world = verify_world(source, systems)
    destination_world = verify_world(destination, systems)

    return Baggage(source_world, destination_world)
