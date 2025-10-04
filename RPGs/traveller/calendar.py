"""Contains classes for tracking time in the game.

Calendar - keeps track of the current date, and notifies
           observers when it changes.
ImperialDate - represents a single date Traveller format: DDD-YYYY
"""

class Calendar:
    """Tracks the current date and notifies observers when it changes."""

    def __init__(self):
        self.current_date = ImperialDate(1,1105)
        self.observers = []

    @property
    def day(self):
        return self.current_date.day

    @day.setter
    def day(self, value):
        self.current_date.day = value
        # this is redundant with logic in ImperialDate - review
        if self.current_date.day >= 366:
            self.current_date.day = self.day - 365
            self.year += 1
        for observer in self.observers:
            observer.notify(self.current_date)

    @property
    def year(self):
        return self.current_date.year

    @year.setter
    def year(self, value):
        self.current_date.year = value
        for observer in self.observers:
            observer.notify(self.current_date)

    def plus_week(self):
        self.day += 7

    def __repr__(self):
        return f"{self.current_date}"

    def add_observer(self, observer):
        self.observers.append(observer)

class ImperialDate:
    """Represents a single date in Travller format: DDD-YYYY."""

    def __init__(self, day, year):
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

    def __repr__(self):
        return f"{self.day:03.0f}-{self.year}"

    def __eq__(self, other):
        if type(other) is type(self):
            return self.day == other.day and self.year == other.year
        return NotImplemented

    def __gt__(self, other):
        return self.year > other.year or (self.day > other.day and
                                          self.year == other.year)

    def __ge__(self, other):
        return self == other or self > other

    def _date_value(self):
        return self.day + (self.year * 365)

    def __sub__(self, other):
        if isinstance(other, ImperialDate):
            return self._date_value() - other._date_value()
        if isinstance(other, int):
            return ImperialDate(self.day - other, self.year)
        return NotImplemented

    def __add__(self, days):
        return ImperialDate(self.day + days, self.year)

    def copy(self):
        return ImperialDate(self.day, self.year)

