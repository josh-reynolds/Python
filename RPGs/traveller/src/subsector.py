"""Contains the Subsector class and a factory function.

Subsector - represents a Traveller subsector.

subsector_from() - create a Subsector object from a string representation.
"""
from typing import Tuple, Any
from src.utilities import get_tokens

class Subsector:
    """Represents a Traveller subsector."""

    # TO_DO: we now have subsectors in a hash by coordinate, so
    #        the field is redundant and this class is reduced to a
    #        simple string... consider killing it
    def __init__(self, name: str, coordinate: Tuple[int, int]) -> None:
        """Create an instance of a Subsector."""
        self.name = name
        self.coordinate = coordinate

    def __str__(self) -> str:
        """Return the string representation of a Subsector object."""
        return self.name

    def __repr__(self) -> str:
        """Return the developer string representation of a Subsector object."""
        return f"Subsector({self.name}, {self.coordinate})"

    def __eq__(self, other: Any) -> bool:
        """Test whether two Subsector objects are equal."""
        if type(other) is type(self):
            return self.coordinate == other.coordinate and self.name == other.name
        return NotImplemented


def subsector_from(string: str) -> Subsector:
    """Create a Subsector object from a string representation.

    String format matches the 'subsectors' section of the output
    of PlayScreen.save_game(), which is comprised of a coordinate tuple
    and subsector name.

    Coordinate - Subsector Name
    (d,d) - w*
    Coordinate digits are +/- integers.
    """
    tokens = get_tokens(string, 2, 2)

    coord_str = tokens[0]
    coord_str = coord_str[1:-1]     # remove surrounding parentheses
    coord = tuple(int(n) for n in coord_str.split(','))

    if len(coord) != 2:
        raise ValueError(f"coordinate should have exactly two integers: '{coord}'")

    # generator produces tuple[int, ...] but ctor expects tuple[int, int]
    # mypy doesn't know the string should have just two members
    return Subsector(tokens[1], coord)   # type: ignore[arg-type]
