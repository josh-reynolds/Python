"""Contains tests for the financials module."""
from __future__ import annotations
import unittest
from typing import Any
from calendar import ImperialDate
from financials import Credits, Financials, financials_from
from mock import ObserverMock

class CreditsTestCase(unittest.TestCase):
    """Tests Credits class."""

    def test_credits_string(self) -> None:
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

    def test_credits_comparison(self) -> None:
        """Tests comparison of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(2)
        credits3 = Credits(2)
        self.assertGreater(credits2,credits1)
        self.assertLess(credits1,credits2)
        self.assertEqual(credits2,credits3)

    def test_credits_addition(self) -> None:
        """Tests addition of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(1)
        self.assertEqual(credits1+credits2,Credits(2))

    def test_credits_subtraction(self) -> None:
        """Tests subtraction of two Credits objects."""
        credits1 = Credits(1)
        credits2 = Credits(2)
        self.assertEqual(credits2-credits1,Credits(1))

    def test_credits_multiplication(self) -> None:
        """Tests multiplication of a Credits object by an integer."""
        credits1 = Credits(10)
        self.assertEqual(credits1 * 5, Credits(50))

class FinancialsTestCase(unittest.TestCase):
    """Tests Financials class."""

    financials: Financials

    class DateMock(ImperialDate):
        """Mocks a date interface for testing."""

        def __init__(self, value: int) -> None:
            """Create an instance of a DateMock object."""
            super().__init__(value, value)
            self.value = value

        def copy(self) -> FinancialsTestCase.DateMock:
            """Return a copy of this DateMock object."""
            return FinancialsTestCase.DateMock(self.value)

        def __add__(self, rhs: int) -> FinancialsTestCase.DateMock:
            """Add a value to a DateMock."""
            return FinancialsTestCase.DateMock(self.value + rhs)

        def __sub__(self, rhs: Any) -> FinancialsTestCase.DateMock | int:
            """Subtract either a DateMock or an integer from a DateMock."""
            if isinstance(rhs, FinancialsTestCase.DateMock):
                return self.value - rhs.value
            if isinstance(rhs, int):
                return FinancialsTestCase.DateMock(self.value - rhs)
            return NotImplemented

        def __eq__(self, other: Any) -> bool:
            """Test whether two DateMocks are equivalent."""
            return self.value == other.value

        def __ge__(self, other: Any) -> bool:
            """Test whether one DateMock is greater than or equal to another."""
            return self.value >= other.value

        def __gt__(self, other: Any) -> bool:
            """Test whether one DateMock is greater than another."""
            return self.value > other.value

        def __str__(self) -> str:
            """Return the string representation of a DateMock object."""
            return f"{self.value}"

        def __repr__(self) -> str:
            """Return the developer string representation of a DateMock object."""
            return f"DateMock({self.value})"

    class ShipMock:
        """Mocks a ship interface for testing."""

        def __init__(self) -> None:
            """Create an instance of a ShipMock object."""
            self.last_maintenance = FinancialsTestCase.DateMock(1)

        def crew_salary(self) -> Credits:
            """Return the amount of monthly salary paid to the Ship's crew."""
            return Credits(1)

        def loan_payment(self) -> Credits:
            """Return the amount paid monthly for the Ship's loan."""
            return Credits(1)

    # pylint: disable=R0903
    # R0903: Too few public methods (1/2)
    class SystemMock:
        """Mocks a system interface for testing."""

        def __init__(self) -> None:
            """Create an instance of a SystemMock object."""
            self.name = "MOCK"

        def on_surface(self) -> bool:
            """Test whether the player is on the world's surface."""
            return True

        def __str__(self) -> str:
            """Return the string representation of a SystemMock object."""
            return self.name

    def setUp(self) -> None:
        """Create a test fixture for validating the Financials class."""
        FinancialsTestCase.financials = Financials(100,
                                                   FinancialsTestCase.DateMock(1),
                                                   FinancialsTestCase.ShipMock(),
                                                   FinancialsTestCase.SystemMock())

    def test_on_notify(self) -> None:
        """Test notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        date = FinancialsTestCase.DateMock(8)
        financials.on_notify(date)
        self.assertEqual(financials.current_date, date)
        self.assertEqual(observer.message, "Renewing berth on 8 for 7 days (700 Cr).")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(16)
        financials.on_notify(date)
        self.assertEqual(financials.current_date, date)
        self.assertEqual(observer.message, "Renewing berth on 16 for 2 days (200 Cr).")
        self.assertEqual(observer.priority, "")

    def test_debit_and_credit(self) -> None:
        """Test debiting and crediting a balance managed by a Financials object."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))

        financials.debit(Credits(10))
        self.assertEqual(financials.balance, Credits(90))

        financials.credit(Credits(20))
        self.assertEqual(financials.balance, Credits(110))

    # pylint: disable=W0212
    # W0212: Access to a protected member _salary_notification of a client class
    def test_salary_notification(self) -> None:
        """Test salary notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(1))

        date = FinancialsTestCase.DateMock(30)
        financials._salary_notification(date)
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(29))
        self.assertEqual(observer.message, "Paying crew salaries on 29 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(60)
        financials._salary_notification(date)
        self.assertEqual(financials.balance, Credits(98))
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(57))
        self.assertEqual(observer.message, "Paying crew salaries on 57 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(120)
        financials._salary_notification(date)
        self.assertEqual(financials.balance, Credits(96))
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(113))
        self.assertEqual(observer.message, "Paying crew salaries on 113 for 1 Cr.")
        self.assertEqual(observer.priority, "")

    # pylint: disable=W0212
    # W0212: Access to a protected member _pay_salaries of a client class
    def test_pay_salaries(self) -> None:
        """Test paying monthly crew salaries."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.balance, Credits(100))

        financials._pay_salaries()
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(observer.message, "Paying crew salaries on 1 for 1 Cr.")
        self.assertEqual(observer.priority, "")

    # pylint: disable=W0212
    # W0212: Access to a protected member _loan_notification of a client class
    def test_loan_notification(self) -> None:
        """Test loan notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(1))

        date = FinancialsTestCase.DateMock(30)
        financials._loan_notification(date)
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(29))
        self.assertEqual(observer.message, "Paying ship loan on 29 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(60)
        financials._loan_notification(date)
        self.assertEqual(financials.balance, Credits(98))
        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(57))
        self.assertEqual(observer.message, "Paying ship loan on 57 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(120)
        financials._loan_notification(date)
        self.assertEqual(financials.balance, Credits(96))
        self.assertEqual(financials.loan_paid, FinancialsTestCase.DateMock(113))
        self.assertEqual(observer.message, "Paying ship loan on 113 for 1 Cr.")
        self.assertEqual(observer.priority, "")

    # pylint: disable=W0212
    # W0212: Access to a protected member _pay_loan of a client class
    def test_pay_loan(self) -> None:
        """Test monthly load payment."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.balance, Credits(100))

        financials._pay_loan()
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(observer.message, "Paying ship loan on 1 for 1 Cr.")
        self.assertEqual(observer.priority, "")

    # pylint: disable=W0212
    # W0212: Access to a protected member _maintenance_notification of a client class
    def test_maintenance_notification(self) -> None:
        """Test maintenance behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.last_maintenance, FinancialsTestCase.DateMock(-13))

        date = FinancialsTestCase.DateMock(30)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(296)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(297)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "Days since last maintenance = 310")
        self.assertEqual(observer.priority, "yellow")

        date = FinancialsTestCase.DateMock(352)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "Days since last maintenance = 365")
        self.assertEqual(observer.priority, "yellow")

        date = FinancialsTestCase.DateMock(353)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "Days since last maintenance = 366")
        self.assertEqual(observer.priority, "red")

    def test_maintenance_status(self) -> None:
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

    def test_berthing_fee(self) -> None:
        """Test payment of starport berthing fees."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 6)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))

        financials.berthing_fee(False)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 6)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        financials.berthing_fee(True)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(7))
        self.assertEqual(observer.message, "Charging 100 Cr berthing fee.")
        self.assertEqual(observer.priority, "")

    # pylint: disable=W0212
    # W0212: Access to a protected member _berth_notification of a client class
    def test_berth_notification(self) -> None:
        """Test berth notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 6)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))

        date = FinancialsTestCase.DateMock(7)
        financials.location.on_surface = lambda : False
        financials._berth_notification(date)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 6)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        financials.location.on_surface = lambda : True
        financials.berth_recurrence = 1
        financials.berth_expiry = financials.current_date + 6
        date = FinancialsTestCase.DateMock(8)
        financials._berth_notification(date)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(9))
        self.assertEqual(observer.message, "Renewing berth on 8 for 1 day (100 Cr).")
        self.assertEqual(observer.priority, "")

    # pylint: disable=W0212
    # W0212: Access to a protected member _renew_berth of a client class
    def test_renew_berth(self) -> None:
        """Test berth renewal."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 6)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(1))
        self.assertEqual(financials.current_date,
                         FinancialsTestCase.DateMock(1))

        financials.berth_recurrence = 1
        financials.berth_expiry = financials.current_date + 6
        date = FinancialsTestCase.DateMock(7)
        financials._renew_berth(date)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(7))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        date = FinancialsTestCase.DateMock(8)
        financials._renew_berth(date)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         FinancialsTestCase.DateMock(9))
        self.assertEqual(observer.message, "Renewing berth on 8 for 1 day (100 Cr).")
        self.assertEqual(observer.priority, "")

    def test_ledger(self) -> None:
        """Test recording of transactions in ledger."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(len(financials.ledger), 0)

        financials.debit(Credits(10), "test")
        self.assertEqual(financials.balance, Credits(90))
        self.assertEqual(len(financials.ledger), 1)
        self.assertEqual(financials.ledger[0], "1\t - 10 Cr\t - \t\t - 90 Cr\t - MOCK\t - test")

        financials.credit(Credits(100), "test")
        self.assertEqual(financials.balance, Credits(190))
        self.assertEqual(len(financials.ledger), 2)
        self.assertEqual(financials.ledger[1], "1\t - \t\t - 100 Cr\t - 190 Cr\t - MOCK\t - test")

        date = FinancialsTestCase.DateMock(2)
        financials.on_notify(date)
        self.assertEqual(financials.balance, Credits(90))
        self.assertEqual(len(financials.ledger), 3)
        self.assertEqual(financials.ledger[2], "2\t - 100 Cr\t - \t\t - "
                                               + "90 Cr\t - MOCK\t - berth renewal")

    # pylint: disable=R0915
    # R0915: Too many statements (61/50)
    def test_financials_from(self) -> None:
        """Test importing a Financials object from a string."""
        string = "100 - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        actual = financials_from(string)
        expected = Financials(100, ImperialDate(1,1105), None, None)
        self.assertEqual(actual, expected)

        string = "200 - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        actual = financials_from(string)
        expected = Financials(200, ImperialDate(1,1105), None, None)
        self.assertEqual(actual, expected)

        string = "100 - 001-1106 - 001-1106 - 001-1106 - 001-1106 - 352-1105"
        actual = financials_from(string)
        expected = Financials(100, ImperialDate(1,1106), None, None)
        self.assertEqual(actual, expected)

        string = "999 - 010-1105 - 004-1105 - 010-1105 - 010-1105 - 361-1104"
        actual = financials_from(string)
        expected = Financials(999, ImperialDate(10,1105), None, None)
        expected.berth_expiry = ImperialDate(4,1105)
        self.assertEqual(actual, expected)

        string = "1 - 010-1105 - 010-1105 - 004-1105 - 010-1105 - 361-1104"
        actual = financials_from(string)
        expected = Financials(1, ImperialDate(10,1105), None, None)
        expected.salary_paid = ImperialDate(4,1105)
        self.assertEqual(actual, expected)

        string = "1000 - 010-1105 - 010-1105 - 010-1105 - 004-1105 - 361-1104"
        actual = financials_from(string)
        expected = Financials(1000, ImperialDate(10,1105), None, None)
        expected.loan_paid = ImperialDate(4,1105)
        self.assertEqual(actual, expected)

        string = "1000000 - 010-1105 - 010-1105 - 010-1105 - 010-1105 - 100-1104"
        actual = financials_from(string)
        expected = Financials(1_000_000, ImperialDate(10,1105), None, None)
        expected.last_maintenance = ImperialDate(100,1104)
        self.assertEqual(actual, expected)

        string = "1000 - 010-1105 - 010-1105 - 010-1105 - 004-1105 - 361-1104 - 0000"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "input string has extra data: "
                         + "'1000 - 010-1105 - 010-1105 - 010-1105 - 004-1105 - 361-1104 - 0000'")

        string = "1000 - 010-1105 - 010-1105 - 010-1105 - 004-1105"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "input string is missing data: "
                         + "'1000 - 010-1105 - 010-1105 - 010-1105 - 004-1105'")

        string = "-100 - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "balance must be a positive integer: '-100'")

        string = "m - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "100 - 001 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "string must have both day and year values: '001'")

        string = "100 - 001-1105-1 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "string must have only day and year values: '001-1105-1'")

        string = "100 - 366-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "day value must be between 1 and 365: '366'")

        # no need to repeat date validation for all of them - this is covered
        # in test cases for imperial_date_from(), which used across the board


        string = "100 - 010-1105 - 001-1105 - 010-1105 - 010-1105 - 361-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "berth expiry value cannot be more than " +
                         "six days before current date: '001-1105'")

        string = "100 - 010-1105 - 017-1105 - 010-1105 - 010-1105 - 361-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "berth expiry value cannot be more than " +
                         "six days from current date: '017-1105'")

        string = "100 - 010-1105 - 010-1105 - 346-1104 - 010-1105 - 361-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "salary paid value cannot be more than twenty eight " +
                         "days before current date: '346-1104'")

        string = "100 - 010-1105 - 010-1105 - 011-1105 - 010-1105 - 361-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "salary paid value cannot be later than the current date: '011-1105'")

        string = "100 - 010-1105 - 010-1105 - 010-1105 - 346-1104 - 361-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "loan paid value cannot be more than twenty eight " +
                         "days before current date: '346-1104'")

        string = "100 - 010-1105 - 010-1105 - 010-1105 - 011-1105 - 361-1104"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "loan paid value cannot be later than the current date: '011-1105'")

        # invalid last_maintenance - must be legal date format
        #                            can't be more than current_date

    def test_encode(self) -> None:
        """Test exporting a Financials object to a string."""
        financials = Financials(100, ImperialDate(1,1105), None, None)
        actual = financials.encode()
        expected = "100 - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        self.assertEqual(actual, expected)

        financials = Financials(200, ImperialDate(1,1105), None, None)
        actual = financials.encode()
        expected = "200 - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        self.assertEqual(actual, expected)

        financials = Financials(300, ImperialDate(1,1106), None, None)
        actual = financials.encode()
        expected = "300 - 001-1106 - 001-1106 - 001-1106 - 001-1106 - 352-1105"
        self.assertEqual(actual, expected)

        financials = Financials(999, ImperialDate(10,1105), None, None)
        financials.berth_expiry = ImperialDate(4,1105)
        actual = financials.encode()
        expected = "999 - 010-1105 - 004-1105 - 010-1105 - 010-1105 - 361-1104"
        self.assertEqual(actual, expected)

        financials = Financials(1, ImperialDate(10,1105), None, None)
        financials.salary_paid = ImperialDate(4,1105)
        actual = financials.encode()
        expected = "1 - 010-1105 - 010-1105 - 004-1105 - 010-1105 - 361-1104"
        self.assertEqual(actual, expected)

        financials = Financials(1000, ImperialDate(10,1105), None, None)
        financials.loan_paid = ImperialDate(4,1105)
        actual = financials.encode()
        expected = "1000 - 010-1105 - 010-1105 - 010-1105 - 004-1105 - 361-1104"
        self.assertEqual(actual, expected)

        financials = Financials(1_000_000, ImperialDate(10,1105), None, None)
        financials.last_maintenance = ImperialDate(100,1104)
        actual = financials.encode()
        expected = "1000000 - 010-1105 - 010-1105 - 010-1105 - 010-1105 - 100-1104"
        self.assertEqual(actual, expected)


# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
