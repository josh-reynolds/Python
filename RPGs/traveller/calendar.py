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
        if self.day > 365:
            self.day -= 365
            self.year += 1

    def __repr__(self):
        return f"{self.day:03.0f}-{self.year}"

    def __eq__(self, other):
        return self.day == other.day and self.year == other.year

    def __gt__(self, other):
        return self.year > other.year or (self.day > other.day and
                                          self.year == other.year)

    def __ge__(self, other):
        return self == other or self > other

    # BUG: does not work correctly across year boundary
    def __sub__(self, other):
        return self.day - other.day

    # BUG: ctor handles positive year boundary, but not negative,
    #      what if we added a negative number of days?
    def __add__(self, days):
        return ImperialDate(self.day + days, self.year)

    def copy(self):
        return ImperialDate(self.day, self.year)

class ImperialDateTestCase(unittest.TestCase):
    def test_date_plus_day(self):
        a = ImperialDate(1,100)
        b = a + 1
        self.assertEqual(b.day, 2)
        self.assertEqual(b.year, 100)
        self.assertEqual(b, ImperialDate(2,100))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
