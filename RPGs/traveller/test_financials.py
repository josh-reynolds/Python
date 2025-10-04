"""Contains tests for the financials module."""
import unittest
from financials import Credits, Financials

class CreditsTestCase(unittest.TestCase):
    """Tests Credits class."""

    def test_credits_string(self):
        """Tests string representation of a Credits object."""
        credits1 = Credits(1)
        credits2 = Credits(10)
        credits3 = Credits(100)
        credits4 = Credits(1000)
        credits5 = Credits(10000)
        credits6 = Credits(100000)
        credits7 = Credits(1000000)
        credits8 = Credits(11500000)
        credits9 = Credits(1000000000)
        self.assertEqual(f"{credits1}", "1 Cr")
        self.assertEqual(f"{credits2}", "10 Cr")
        self.assertEqual(f"{credits3}", "100 Cr")
        self.assertEqual(f"{credits4}", "1,000 Cr")
        self.assertEqual(f"{credits5}", "10,000 Cr")
        self.assertEqual(f"{credits6}", "100,000 Cr")
        self.assertEqual(f"{credits7}", "1.0 MCr")
        self.assertEqual(f"{credits8}", "11.5 MCr")
        self.assertEqual(f"{credits9}", "1,000.0 MCr")

    def test_credits_comparison(self):
        """Tests comparison of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(2)
        credits3 = Credits(2)
        self.assertGreater(credits2,credits1)
        self.assertLess(credits1,credits2)
        self.assertEqual(credits2,credits3)

    def test_credits_addition(self):
        """Tests addition of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(1)
        self.assertEqual(credits1+credits2,Credits(2))

    def test_credits_subtraction(self):
        """Tests subtraction of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(2)
        self.assertEqual(credits2-credits1,Credits(1))

    def test_credits_multiplication(self):
        """Tests multiplication of a Credits object by an integer."""
        credits1 = Credits(10)
        self.assertEqual(credits1 * 5, Credits(50))

class FinancialsTestCase(unittest.TestCase):
    """Tests Financials class."""

    class DateMock:
        """Mocks a date interface for testing."""

        def __init__(self, value):
            """Create an instance of a DateMock object."""
            self.value = value

        def copy(self):
            """Return a copy of this DateMock object."""
            return FinancialsTestCase.DateMock(self.value)

        def __add__(self, rhs):
            """Add a value to a DateMock."""
            return FinancialsTestCase.DateMock(self.value + rhs)

        def __sub__(self, rhs):
            """Subtract either a DateMock or an integer from a DateMock."""
            if isinstance(rhs, FinancialsTestCase.DateMock):
                return self.value - rhs.value
            if isinstance(rhs, int):
                return FinancialsTestCase.DateMock(self.value - rhs)
            return NotImplemented

        def __eq__(self, other):
            """Test whether two DateMocks are equivalent."""
            return self.value == other.value

        def __ge__(self, other):
            """Test whether one DateMock is greater than or equal to another."""
            return self.value >= other.value

        def __gt__(self, other):
            """Test whether one DateMock is greater than another."""
            return self.value > other.value

        def __repr__(self):
            """Return the string representation of a DateMock object."""
            return f"{self.value}"

    class ShipMock:
        """Mocks a ship interface for testing."""

        def __init__(self):
            """Create an instance of a ShipMock object."""
            self.last_maintenance = FinancialsTestCase.DateMock(1)

        def crew_salary(self):
            """Return the amount of monthly salary paid to the Ship's crew."""
            return Credits(1)

        def loan_payment(self):
            """Return the amount paid monthly for the Ship's loan."""
            return Credits(1)

    class SystemMock:
        """Mocks a system interface for testing."""

        def on_surface(self):
            """Test whether the player is on the world's surface."""
            return True

    def setUp(self):
        """Create a test fixture for validating the Financials class."""
        FinancialsTestCase.financials = Financials(100,
                                                   FinancialsTestCase.DateMock(1),
                                                   FinancialsTestCase.ShipMock(),
                                                   FinancialsTestCase.SystemMock())

    @unittest.skip("test has side effects: printing")
    def test_notify(self):
        """Test notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials

        date = FinancialsTestCase.DateMock(8)
        financials.notify(date)
        self.assertEqual(financials.current_date, date)

        date = FinancialsTestCase.DateMock(12)
        financials.notify(date)
        self.assertEqual(financials.current_date, date)

    def test_debit_and_credit(self):
        """Test debiting and crediting a balance managed by a Financials object."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))

        financials.debit(Credits(10))
        self.assertEqual(financials.balance, Credits(90))

        financials.credit(Credits(20))
        self.assertEqual(financials.balance, Credits(110))

    @unittest.skip("test has side effects: printing")
    def test_salary_notification(self):
        """Test salary notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(1))

        date = FinancialsTestCase.DateMock(30)
        financials.salary_notification(date)
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(29))

        date = FinancialsTestCase.DateMock(60)
        financials.salary_notification(date)
        self.assertEqual(financials.balance, Credits(98))
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(57))

        date = FinancialsTestCase.DateMock(120)
        financials.salary_notification(date)
        self.assertEqual(financials.balance, Credits(96))
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(113))

    @unittest.skip("test has side effects: printing")
    def test_pay_salaries(self):
        """Test paying monthly crew salaries."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))

        financials.pay_salaries()
        self.assertEqual(financials.balance, Credits(99))

    @unittest.skip("test has side effects: printing")
    def test_loan_notification(self):
        """Test loan notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(1))

        date = FinancialsTestCase.DateMock(30)
        financials.loan_notification(date)
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(29))

        date = FinancialsTestCase.DateMock(60)
        financials.loan_notification(date)
        self.assertEqual(financials.balance, Credits(98))
        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(57))

        date = FinancialsTestCase.DateMock(120)
        financials.loan_notification(date)
        self.assertEqual(financials.balance, Credits(96))
        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(113))

    @unittest.skip("test has side effects: printing")
    def test_pay_loan(self):
        """Test monthly load payment."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))

        financials.pay_loan()
        self.assertEqual(financials.balance, Credits(99))

    @unittest.skip("test has side effects: printing")
    def test_maintenance_notification(self):
        """Test maintenance behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.last_maintenance, FinancialsTestCase.DateMock(-13))

        date = FinancialsTestCase.DateMock(30)
        financials.maintenance_notification(date)

        date = FinancialsTestCase.DateMock(296)
        financials.maintenance_notification(date)

        date = FinancialsTestCase.DateMock(297)
        financials.maintenance_notification(date)

        date = FinancialsTestCase.DateMock(352)
        financials.maintenance_notification(date)

        date = FinancialsTestCase.DateMock(353)
        financials.maintenance_notification(date)

    def test_maintenance_status(self):
        """Test maintenance status notification."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.last_maintenance, FinancialsTestCase.DateMock(-13))

        date = FinancialsTestCase.DateMock(30)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "green")

        date = FinancialsTestCase.DateMock(296)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "green")

        date = FinancialsTestCase.DateMock(297)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "yellow")

        date = FinancialsTestCase.DateMock(352)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "yellow")

        date = FinancialsTestCase.DateMock(353)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "red")

    @unittest.skip("test has side effects: printing")
    def test_berthing_fee(self):
        """Test payment of starport berthing fees."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, None)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))

        financials.berthing_fee(False)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, None)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))

        financials.berthing_fee(True)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(7))

    @unittest.skip("test has side effects: printing")
    def test_berth_notification(self):
        """Test berth notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, None)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))

        date = FinancialsTestCase.DateMock(7)
        financials.location.on_surface = lambda : False
        financials.berth_notification(date)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, None)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))

        financials.location.on_surface = lambda : True
        financials.berth_recurrence = 1
        financials.berth_expiry = financials.current_date + 6
        date = FinancialsTestCase.DateMock(8)
        financials.berth_notification(date)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(9))

    @unittest.skip("test has side effects: printing")
    def test_renew_berth(self):
        """Test berth renewal."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, None)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))

        financials.berth_recurrence = 1
        financials.berth_expiry = financials.current_date + 6
        date = FinancialsTestCase.DateMock(7)
        financials.renew_berth(date)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(7))

        date = FinancialsTestCase.DateMock(8)
        financials.renew_berth(date)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(9))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
