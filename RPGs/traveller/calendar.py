"""Contains classes for tracking time in the game.

Calendar - keeps track of the current date, and notifies
           observers when it changes.
ImperialDate - represents a single date Traveller format: DDD-YYYY
"""
import unittest

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

class ImperialDateTestCase(unittest.TestCase):
    """Tests ImperialDate class."""

    def test_date_string(self):
        date = ImperialDate(1,100)
        self.assertEqual(f"{date}", "001-100")

    def test_date_equality(self):
        date1 = ImperialDate(1,100)
        date2 = ImperialDate(1,100)
        date3 = ImperialDate(2,100)
        self.assertEqual(date1,date2)
        self.assertNotEqual(date1,date3)
        self.assertNotEqual(date2,date3)
        self.assertNotEqual(date1,(1,100))

    def test_date_comparison(self):
        date1 = ImperialDate(10,100)
        date2 = ImperialDate(11,100)
        date3 = ImperialDate(1,101)
        date4 = ImperialDate(20,99)
        date5 = ImperialDate(1,100)
        self.assertGreater(date2,date1)
        self.assertGreater(date3,date1)
        self.assertLess(date4,date1)
        self.assertLess(date5,date1)

    def test_date_copy(self):
        date1 = ImperialDate(1,100)
        date2 = date1.copy()
        self.assertEqual(date2.day, 1)
        self.assertEqual(date2.year, 100)
        self.assertEqual(date1,date2)

    def test_date_plus_days(self):
        date1 = ImperialDate(1,100)
        date2 = ImperialDate(365,100)
        self.assertEqual(date1 + 1, ImperialDate(2,100))
        self.assertEqual(date2 + 1, ImperialDate(1,101))
        self.assertEqual(date1 + -1, ImperialDate(365,99))
        self.assertEqual(date2 + -1, ImperialDate(364,100))
        self.assertEqual(date1 + -10, ImperialDate(356,99))

    def test_date_minus_date(self):
        date1 = ImperialDate(1,100)
        date2 = ImperialDate(5,100)
        date3 = ImperialDate(365,99)
        date4 = ImperialDate(1,98)
        self.assertEqual(date2-date1, 4)
        self.assertEqual(date1-date2, -4)
        self.assertEqual(date1-date3, 1)
        self.assertEqual(date3-date1, -1)
        self.assertEqual(date1-date4, 730)

    def test_date_minus_day(self):
        date1 = ImperialDate(5,100)
        self.assertEqual(date1-1, ImperialDate(4,100))
        self.assertEqual(date1-5, ImperialDate(365,99))

class CalendarTestCase(unittest.TestCase):
    """Tests Calendar class."""

    class ObserverMock:
        """Mocks an observer interface for testing."""

        def __init__(self):
            self.paid_date = ImperialDate(365,1104)
            self.count = 0
            self.event_count = 0
            self.recurrence = 1
        def notify(self, date):
            self.count += 1
            duration = (date - self.paid_date) // self.recurrence
            for _ in range(duration):
                self.event_count += 1
                self.paid_date += self.recurrence

    def setUp(self):
        CalendarTestCase.a = Calendar()
        CalendarTestCase.a.add_observer(CalendarTestCase.ObserverMock())

    def test_recurring_events_from_notification(self):
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        calendar.plus_week()
        self.assertEqual(calendar.current_date, ImperialDate(8,1105))
        self.assertEqual(mock.count, 1)
        self.assertEqual(mock.event_count, 8)
        self.assertEqual(mock.paid_date, ImperialDate(8,1105))

    def test_longer_recurrence_than_daily(self):
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        mock.recurrence = 3
        calendar.plus_week()
        self.assertEqual(calendar.current_date, ImperialDate(8,1105))
        self.assertEqual(mock.count, 1)
        self.assertEqual(mock.event_count, 2)
        self.assertEqual(mock.paid_date, ImperialDate(6,1105))

    def test_day_property(self):
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)

        calendar.day += 1
        self.assertEqual(calendar.day, 2)
        self.assertEqual(mock.count, 1)

        calendar.day += 364
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1106)

    def test_year_property(self):
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)

        calendar.year += 1
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1106)
        self.assertEqual(mock.count, 1)

    def test_plus_week(self):
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)

        calendar.plus_week()
        self.assertEqual(calendar.day, 8)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 1)

    def test_calendar_string(self):
        calendar = CalendarTestCase.a
        self.assertEqual(f"{calendar}", "001-1105")

    def test_add_observer(self):
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)
        self.assertEqual(len(calendar.observers), 1)

        calendar.add_observer(CalendarTestCase.ObserverMock())
        self.assertEqual(len(calendar.observers), 2)

        calendar.plus_week()
        self.assertEqual(calendar.day, 8)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 1)
        self.assertEqual(calendar.observers[1].count, 1)

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
