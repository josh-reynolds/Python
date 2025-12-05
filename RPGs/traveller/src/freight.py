"""Contains the Freight class and a factory function.

Freight - represents bulk freight.

freight_from() - creates a Freight object from a parsed source string.
"""
from typing import Any, Mapping
from src.coordinate import Coordinate
from src.star_system import StarSystem, Hex, verify_world

class Freight:
    """Represents bulk freight."""

    def __init__(self, tonnage: int,
                 source_world: StarSystem, destination_world: StarSystem) -> None:
        """Create an instance of a Freight shipment."""
        self.name = "Freight"
        self.tonnage = tonnage
        self.source_world = source_world
        self.destination_world = destination_world

    def __str__(self) -> str:
        """Return a formatted string for a given Freight shipment."""
        if self.tonnage > 1:
            unit = "tons"
        else:
            unit = "ton"
        return f"{self.name} : {self.tonnage} {unit} : " +\
               f"{self.source_world.name} -> {self.destination_world.name}"

    def __repr__(self) -> str:
        """Return the developer string representation of a Freight shipment."""
        return f"Freight({self.tonnage}, {self.source_world!r}, {self.destination_world!r})"

    def __eq__(self, other: Any) -> bool:
        """Test if two Freight objects are equal."""
        if type(other) is type(self):
            return self.tonnage == other.tonnage and self.source_world == other.source_world \
                    and self.destination_world == other.destination_world
        return NotImplemented

    def encode(self) -> str:
        """Return a string encoding the Freight object to save and load state."""
        return f"Freight - {self.tonnage} - {self.source_world.coordinate} " +\
               f"- {self.destination_world.coordinate}"


def freight_from(tonnage: int, source: str, destination: str,
                 systems: Mapping[Coordinate, Hex]) -> Freight:
    """Create a Freight object from a parsed source string.

    Both coordinate arguments are in the format : (d,d,d), all +/- integers.

    The function also needs access to a dictionary of StarSystems, and
    the coordinates must be keys in that dictionary.
    """
    if tonnage < 1:
        raise ValueError(f"tonnage must be a positive number: '{tonnage}'")

    source_world = verify_world(source, systems)
    destination_world = verify_world(destination, systems)

    return Freight(tonnage, source_world, destination_world)
