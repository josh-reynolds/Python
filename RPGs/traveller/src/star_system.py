"""Contains classes to represent Traveller star map hexes.

Hex - base class for map hexes.

DeepSpace - represents an empty map hex.

StarSystem - represents a map hex containing a star system.

verify_world() - verify a coordinate refers to a StarSystem.
"""
from abc import ABC, abstractmethod
from typing import List, Any, Mapping, cast
from src.coordinate import Coordinate, coordinate_from
from src.uwp import UWP

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Hex(ABC):
    """Base class for map hexes."""

    def __init__(self, coordinate: Coordinate) -> None:
        """Create an instance of a Hex."""
        self.coordinate = coordinate
        self.name = ""
        self.destinations: List[StarSystem] = []

    @abstractmethod
    def description(self) -> str:
        """Return the descriptor for a Hex object."""


class DeepSpace(Hex):
    """Represents an empty map hex."""

    def __init__(self, coordinate: Coordinate) -> None:
        """Create an instance of a DeepSpace object."""
        super().__init__(coordinate)
        self.location = ""
        self.population = 0
        self.gas_giant = False

    def __str__(self) -> str:
        """Return the string representation of a DeepSpace object."""
        return "Deep Space"

    def __repr__(self) -> str:
        """Return the developer string representation of a DeepSpace object."""
        return f"DeepSpace({repr(self.coordinate)})"

    def __eq__(self, other: Any) -> bool:
        """Test whether two DeepSpace objects are equal."""
        if type(other) is type(self):
            return self.coordinate == other.coordinate
        return NotImplemented

    def description(self) -> str:
        """Return the descriptor for a DeepSpace hex."""
        return "stranded in deep space"


# pylint: disable=R0902
# R0902: Too many instance attributes (10/7)
class StarSystem(Hex):
    """Represents a map hex containing a star system."""

    def __init__(self, name: str, coordinate: Coordinate,
                 uwp: UWP, gas_giant: bool = True) -> None:
        """Create an instance of a StarSystem."""
        super().__init__(coordinate)
        self.name = name
        self.uwp = uwp
        self.gas_giant = gas_giant
        self.location = "orbit"

    @property
    def agricultural(self) -> bool:
        """Test StarSystem for Agricultural trade classification."""
        return self.atmosphere in (4, 5, 6, 7, 8, 9) and\
               self.hydrographics in (4, 5, 6, 7, 8) and\
               self.population in (5, 6, 7)

    @property
    def nonagricultural(self) -> bool:
        """Test StarSystem for Nonagricultural trade classification."""
        return self.atmosphere in (0, 1, 2, 3) and\
               self.hydrographics in (0, 1, 2, 3) and\
               self.population in (6, 7, 8, 9, 10)

    @property
    def industrial(self) -> bool:
        """Test StarSystem for Industrial trade classification."""
        return self.atmosphere in (0, 1, 2, 4, 7, 9) and self.population in (9, 10)

    @property
    def nonindustrial(self) -> bool:
        """Test StarSystem for Nonindustrial trade classification."""
        return self.population in (0, 1, 2, 3, 4, 5, 6)

    @property
    def rich(self) -> bool:
        """Test StarSystem for Rich trade classification."""
        return self.government in (4, 5, 6, 7, 8, 9) and\
               self.atmosphere in (6, 8) and\
               self.population in (6, 7, 8)

    @property
    def poor(self) -> bool:
        """Test StarSystem for Poor trade classification."""
        return self.atmosphere in (2, 3, 4, 5) and self.hydrographics in (0, 1, 2, 3)

    def __eq__(self, other: Any) -> bool:
        """Test whether two StarSystem objects are equal."""
        if type(other) is type(self):
            return self.name == other.name and self.coordinate == other.coordinate and \
                    self.uwp == other.uwp and self.gas_giant == other.gas_giant
        return NotImplemented

    def __hash__(self) -> int:
        """Calculate the hash value for a StarSystem object."""
        return hash((self.coordinate, self.name))

    def __str__(self) -> str:
        """Return the string representation of a StarSystem object."""
        uwp_string = f"{self.uwp}"
        if self.agricultural:
            uwp_string += " Ag"
        if self.nonagricultural:
            uwp_string += " Na"
        if self.industrial:
            uwp_string += " In"
        if self.nonindustrial:
            uwp_string += " Ni"
        if self.rich:
            uwp_string += " Ri"
        if self.poor:
            uwp_string += " Po"
        if self.gas_giant:
            uwp_string += " - G"
        return f"{self.name} - {uwp_string}"

    def __repr__(self) -> str:
        """Return the developer string representation of a StarSystem object."""
        return f"StarSystem(\"{self.name}\", {self.coordinate!r}, {self.uwp!r}, {self.gas_giant})"

    @property
    def starport(self) -> str:
        """Return the UWP starport value."""
        return self.uwp.starport

    @property
    def size(self) -> int:
        """Return the UWP size value."""
        return self.uwp.size

    @property
    def atmosphere(self) -> int:
        """Return the UWP atmosphere value."""
        return self.uwp.atmosphere

    @property
    def hydrographics(self) -> int:
        """Return the UWP hydrographics value."""
        return self.uwp.hydrographics

    @property
    def population(self) -> int:
        """Return the UWP population value."""
        return self.uwp.population

    @property
    def government(self) -> int:
        """Return the UWP government value."""
        return self.uwp.government

    @property
    def law(self) -> int:
        """Return the UWP law level value."""
        return self.uwp.law

    @property
    def tech(self) -> int:
        """Return the UWP tech level value."""
        return self.uwp.tech

    # pylint: disable=R0911
    # R0911: Too many return statements (7/6)
    def description(self) -> str:
        """Return the descriptor for the current location within the StarSystem."""
        if self.location == "starport":
            return f"at the {self.name} starport"

        if self.location == "highport":
            return f"at the {self.name} highport"

        if self.location == "orbit":
            return f"in orbit around {self.name}"

        if self.location == "jump":
            return f"at the {self.name} jump point"

        if self.location == "trade":
            return f"at the {self.name} trade depot"

        if self.location == "terminal":
            return f"at the {self.name} passenger terminal"

        if self.location == "wilderness":
            return f"on the surface of {self.name}"

        return "ERROR"    # should not be able to reach this point
                          # ensure there are only five (currently)
                          # possible values for self.location?

    def at_starport(self) -> bool:
        """Test whether the player is currently berthed at the world's starport."""
        return self.location in ('starport', 'trade', 'terminal', 'highport')


def verify_world(world: str, systems: Mapping[Coordinate, Hex]) -> StarSystem:
    """Verify a coordinate refers to a StarSystem."""
    coordinate = coordinate_from(world)
    if coordinate in systems:
        verified_world = cast(StarSystem, systems[coordinate])
    else:
        raise ValueError(f"coordinate not found in systems list: '{world}'")
    return verified_world
