"""Contains classes and a factory function to handle passengers on a ship.

PassageClass - enum to denote passenger ticket class.
Passenger - represents a passenger on a ship.
passenger_from() - creates a Passenger object from a string representation.
"""
from enum import Enum
from random import randint
from typing import Any, Mapping, cast
from src.coordinate import Coordinate, coordinate_from
from src.credits import Credits
from src.star_system import StarSystem, Hex
from src.utilities import die_roll, get_tokens

class PassageClass(Enum):
    """Denotes the class of a Passenger's ticket."""

    HIGH = 0
    MIDDLE = 1
    LOW = 2


class Passenger:
    """Represents a passenger on a ship."""

    def __init__(self, passage: PassageClass, destination: StarSystem) -> None:
        """Create an instance of a Passenger."""
        if passage == PassageClass.HIGH:
            self.name = "High passage"
            self.ticket_price = Credits(10000)
        if passage == PassageClass.MIDDLE:
            self.name = "Middle passage"
            self.ticket_price = Credits(8000)
        if passage == PassageClass.LOW:
            self.name = "Low passage"
            self.ticket_price = Credits(1000)
        self.passage = passage

        self.destination = destination

        if die_roll(2) < 7:
            self.endurance = -1
        else:
            self.endurance = 0

        self.guess: int | None = None

        self.survived = True

    def __str__(self) -> str:
        """Return a formatted string for a given Passenger."""
        return f"{self.name} to {self.destination.name}"

    def __repr__(self) -> str:
        """Return the developer string representation of a Passenger."""
        return f"Passenger({self.passage!r}, {self.destination!r})"

    def __eq__(self, other: Any) -> bool:
        """Test if two Passengers are equal."""
        if type(other) is type(self):
            return self.passage == other.passage and self.destination == other.destination
        return NotImplemented

    # TO_DO: should be restricted to low passengers only
    def guess_survivors(self, total: int) -> None:
        """Guess the number of low passage survivors."""
        self.guess = randint(0, total)

    def encode(self) -> str:
        """Return a string encoding the Passenger to save and load state."""
        # strip " passage" from the name for encoding
        return f"{self.name[:-8].lower()} - {self.destination.coordinate}"


def passenger_from(string: str, systems: Mapping[Coordinate, Hex]) -> Passenger:
    """Create a Passenger object from a string representation.

    String format is : passage - destination coordinate
    Passage is either 'high,' 'middle,' or 'low.'
    Destination coordinate is (d,d,d), all +/- integers.

    The function also needs access to a dictionary of StarSystems, and
    the coordinate in the string must be a key in that dictionary.
    """
    tokens = get_tokens(string, 2, 2)

    passage_str = tokens[0].lower()
    if passage_str == "high":
        passage = PassageClass.HIGH
    elif passage_str == "middle":
        passage = PassageClass.MIDDLE
    elif passage_str =="low":
        passage = PassageClass.LOW
    else:
        raise ValueError(f"unrecognized passage class: '{passage_str}'")

    coordinate = coordinate_from(tokens[1])
    if coordinate in systems:
        destination = systems[coordinate]
    else:
        raise ValueError(f"coordinate not found in systems list: '{coordinate}'")

    return Passenger(passage, cast(StarSystem, destination))
