import unittest

class Calendar:
    def __init__(self):
        self.current_date = ImperialDate(1,1105)
        self.observers = []

    @property
    def day(self):
        return self.current_date.day

    @day.setter
    def day(self, value):
        self.current_date.day = value
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
        elif isinstance(other, int):
            return ImperialDate(self.day - other, self.year)
        else:
            return NotImplemented

    def __add__(self, days):
        return ImperialDate(self.day + days, self.year)

    def copy(self):
        return ImperialDate(self.day, self.year)

class ImperialDateTestCase(unittest.TestCase):
    def test_date_string(self):
        a = ImperialDate(1,100)
        self.assertEqual(f"{a}", "001-100")

    def test_date_equality(self):
        a = ImperialDate(1,100)
        b = ImperialDate(1,100)
        c = ImperialDate(2,100)
        self.assertEqual(a,b)
        self.assertNotEqual(a,c)
        self.assertNotEqual(b,c)
        self.assertNotEqual(a,(1,100))

    def test_date_comparison(self):
        a = ImperialDate(10,100)
        b = ImperialDate(11,100)
        c = ImperialDate(1,101)
        d = ImperialDate(20,99)
        e = ImperialDate(1,100)
        self.assertGreater(b,a)
        self.assertGreater(c,a)
        self.assertLess(d,a)
        self.assertLess(e,a)

    def test_date_copy(self):
        a = ImperialDate(1,100)
        b = a.copy()
        self.assertEqual(b.day, 1)
        self.assertEqual(b.year, 100)
        self.assertEqual(a,b)

    def test_date_plus_days(self):
        a = ImperialDate(1,100)
        b = ImperialDate(365,100)
        self.assertEqual(a + 1, ImperialDate(2,100))
        self.assertEqual(b + 1, ImperialDate(1,101))
        self.assertEqual(a + -1, ImperialDate(365,99))
        self.assertEqual(b + -1, ImperialDate(364,100))
        self.assertEqual(a + -10, ImperialDate(356,99))

    def test_date_minus_date(self):
        a = ImperialDate(1,100)
        b = ImperialDate(5,100)
        c = ImperialDate(365,99)
        d = ImperialDate(1,98)
        self.assertEqual(b-a, 4)
        self.assertEqual(a-b, -4)
        self.assertEqual(a-c, 1)
        self.assertEqual(c-a, -1)
        self.assertEqual(a-d, 730)

    def test_date_minus_day(self):
        a = ImperialDate(5,100)
        self.assertEqual(a-1, ImperialDate(4,100))
        self.assertEqual(a-5, ImperialDate(365,99))

class CalendarDateTestCase(unittest.TestCase):
    def setUp(self):
        class ObserverMock:
            def __init__(self):
                self.count = 0
            def notify(self, date):
                self.count += 1

        CalendarDateTestCase.a = Calendar()
        CalendarDateTestCase.a.add_observer(ObserverMock())

    def test_notification(self):
        CalendarDateTestCase.a.plus_week()
        count = CalendarDateTestCase.a.observers[0].count
        self.assertEqual(count, 1)

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
