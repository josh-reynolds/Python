"""Contains classes for tracking time in the game.

Calendar - keeps track of the current date, and notifies
           observers when it changes.
ImperialDate - represents a single date in Traveller format: DDD-YYYY
"""
from __future__ import annotations
from typing import Any, List

class Calendar:
    """Tracks the current date and notifies observers when it changes."""

    def __init__(self) -> None:
        """Create an instance of a Calendar."""
        self.current_date = ImperialDate(1,1105)
        self.observers: List[Any] = []

    def __str__(self) -> str:
        """Return the string representation of the current date."""
        return f"{self.current_date}"

    def __repr__(self) -> str:
        """Return the developer string representation of the current date."""
        return "Calendar()"

    @property
    def day(self) -> int:
        """Return the current day."""
        return self.current_date.day

    @day.setter
    def day(self, value: int) -> None:
        """Set the current day and notify all observers."""
        self.current_date.day = value
        # this is redundant with logic in ImperialDate - review
        if self.current_date.day >= 366:
            self.current_date.day = self.day - 365
            self.year += 1
        for observer in self.observers:
            observer.on_notify(self.current_date)

    @property
    def year(self) -> int:
        """Return the current year."""
        return self.current_date.year

    @year.setter
    def year(self, value: int) -> None:
        """Set the current year and notify all observers."""
        self.current_date.year = value
        for observer in self.observers:
            observer.on_notify(self.current_date)

    def add_observer(self, observer: Any) -> None:
        """Add an observer to the calendar.

        The observer is notifed via its on_notify() method
        when the current date changes.
        """
        self.observers.append(observer)

    def plus_week(self) -> None:
        """Move the current day forward by seven days."""
        self.day += 7


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
