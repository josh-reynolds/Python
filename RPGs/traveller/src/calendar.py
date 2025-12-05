"""Contains the Calendar class and a mutator function.

Calendar - keeps track of the current date, and notifies
           observers when it changes.

modify_calendar_from() - modify a Calendar object using 
                         string data.
"""
from typing import Any, List
from src.imperial_date import ImperialDate, imperial_date_from

class Calendar:
    """Tracks the current date and notifies observers when it changes."""

    def __init__(self, current_date: ImperialDate=ImperialDate(1,1105)) -> None:
        """Create an instance of a Calendar."""
        self.current_date = current_date.copy()
        self.observers: List[Any] = []

    def __str__(self) -> str:
        """Return the string representation of the current date."""
        return f"{self.current_date}"

    def __repr__(self) -> str:
        """Return the developer string representation of the current date."""
        return f"Calendar({self.current_date!r})"

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

def modify_calendar_from(calendar: Calendar, string: str) -> None:
    """Modify a Calendar object using a string."""
    new_date = imperial_date_from(string)
    calendar.current_date = new_date
