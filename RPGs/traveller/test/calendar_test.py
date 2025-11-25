"""Contains tests for the calendar module."""
import unittest
from typing import cast
from src.calendar import Calendar, modify_calendar_from
from src.imperial_date import ImperialDate

class CalendarTestCase(unittest.TestCase):
    """Tests Calendar class."""

    a: Calendar

    # pylint: disable=R0903
    # R0903: Too few public methods (1/2)
    class ObserverMock:
        """Mocks an observer interface for testing."""

        def __init__(self) -> None:
            """Create an instance of an ObserverMock."""
            self.paid_date = ImperialDate(365,1104)
            self.count = 0
            self.event_count = 0
            self.recurrence = 1

        def on_notify(self, date: ImperialDate) -> None:
            """On notification from Calendar, track the event."""
            self.count += 1
            duration = cast(int, (date - self.paid_date)) // self.recurrence
            for _ in range(duration):
                self.event_count += 1
                self.paid_date += self.recurrence

    def setUp(self) -> None:
        """Create fixtures for testing."""
        CalendarTestCase.a = Calendar()
        CalendarTestCase.a.add_observer(CalendarTestCase.ObserverMock())

    def test_recurring_events_from_notification(self) -> None:
        """Test repeated Calendar notifications."""
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        calendar.plus_week()
        self.assertEqual(calendar.current_date, ImperialDate(8,1105))
        self.assertEqual(mock.count, 1)
        self.assertEqual(mock.event_count, 8)
        self.assertEqual(mock.paid_date, ImperialDate(8,1105))

    def test_longer_recurrence_than_daily(self) -> None:
        """Test long duration recurrences."""
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        mock.recurrence = 3
        calendar.plus_week()
        self.assertEqual(calendar.current_date, ImperialDate(8,1105))
        self.assertEqual(mock.count, 1)
        self.assertEqual(mock.event_count, 2)
        self.assertEqual(mock.paid_date, ImperialDate(6,1105))

    def test_day_property(self) -> None:
        """Test the day property of a Calendar."""
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

    def test_year_property(self) -> None:
        """Test the year property of a Calendar."""
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)

        calendar.year += 1
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1106)
        self.assertEqual(mock.count, 1)

    def test_plus_week(self) -> None:
        """Test adding a week to a Calendar."""
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)

        calendar.plus_week()
        self.assertEqual(calendar.day, 8)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 1)

    def test_calendar_string(self) -> None:
        """Test the string representation of a Calendar."""
        calendar = CalendarTestCase.a
        self.assertEqual(f"{calendar}", "001-1105")

    def test_add_observer(self) -> None:
        """Test adding an observer to a Calendar."""
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

    def test_modify_from_string(self) -> None:
        """Test modifying a Calendar with a string."""
        calendar = CalendarTestCase.a
        mock = calendar.observers[0]
        self.assertEqual(calendar.day, 1)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)
        self.assertEqual(len(calendar.observers), 1)

        modify_calendar_from(calendar, "002-1105")
        self.assertEqual(calendar.day, 2)
        self.assertEqual(calendar.year, 1105)
        self.assertEqual(mock.count, 0)
