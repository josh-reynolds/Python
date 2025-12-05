"""Contains the Imperial Date class and a factory function.

ImperialDate - represents a single date in Traveller format: DDD-YYYY.

imperial_date_from() - creates an ImperialDate from a formatted string.
"""
from __future__ import annotations
from typing import Any

class ImperialDate:
    """Represents a single date in Traveller format: DDD-YYYY."""

    def __init__(self, day: int, year: int) -> None:
        """Create an instance of an ImperialDate."""
        self.day = day
        self.year = year
        # neither of these will work for large jumps of
        # more than a year
        if self.day > 365:
            self.day -= 365
            self.year += 1
        if self.day < 1:
            self.day += 365
            self.year -= 1

    def __str__(self) -> str:
        """Return the string representation of the date (DDD-YYYY)."""
        return f"{self.day:03.0f}-{self.year}"

    def __repr__(self) -> str:
        """Return the developer string representation of the date."""
        return f"ImperialDate({self.day}, {self.year})"

    def __eq__(self, other: Any) -> bool:
        """Test if two ImperialDates are equal."""
        if type(other) is type(self):
            return self.day == other.day and self.year == other.year
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        """Test if one ImperialDate is greater than another."""
        return self.year > other.year or (self.day > other.day and
                                          self.year == other.year)

    def __ge__(self, other: Any) -> bool:
        """Test if one ImperialDate is greater than or equal to another."""
        return self == other or self > other

    def __add__(self, days: int) -> ImperialDate:
        """Add an integer number of days to an ImperialDate."""
        return ImperialDate(self.day + days, self.year)

    def __sub__(self, other: Any) -> int | ImperialDate:
        """Subtract an ImperialDate or an integer from the date."""
        if isinstance(other, ImperialDate):
            return self._date_value() - other._date_value()
        if isinstance(other, int):
            return ImperialDate(self.day - other, self.year)
        return NotImplemented

    def copy(self) -> ImperialDate:
        """Return a copy of the ImperialDate."""
        return ImperialDate(self.day, self.year)

    def _date_value(self) -> int:
        return self.day + (self.year * 365)

def imperial_date_from(string: str) -> ImperialDate:
    """Create an ImperialDate object from a string representation.

    String format matches ImperialDate.__str__ : ddd-dddd
    """
    tokens = string.split('-')

    if len(tokens) < 2:
        raise ValueError(f"string must have both day and year values: '{string}'")

    if len(tokens) > 2:
        raise ValueError(f"string must have only day and year values: '{string}'")

    day = int(tokens[0])

    if day < 1 or day > 365:
        raise ValueError(f"day value must be between 1 and 365: '{tokens[0]}'")
    year = int(tokens[1])

    return ImperialDate(day, year)
