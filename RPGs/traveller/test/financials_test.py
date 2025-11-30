"""Contains tests for the financials module."""
from __future__ import annotations
import unittest
from test.mock import ObserverMock, ShipMock, SystemMock, DateMock
from src.credits import Credits
from src.imperial_date import ImperialDate
from src.financials import Financials, financials_from

class FinancialsTestCase(unittest.TestCase):
    """Tests Financials class."""

    financials: Financials

    def setUp(self) -> None:
        """Create a test fixture for validating the Financials class."""
        FinancialsTestCase.financials = Financials(100,
                                                   DateMock(1),
                                                   ShipMock( "Type A Free Trader"),
                                                   SystemMock("MOCK"))

    def test_on_notify(self) -> None:
        """Test notification behavior of a Financials object."""
        financials = FinancialsTestCase.financials
        observer = ObserverMock()
        financials.add_observer(observer)

        date = DateMock(8)
        financials.on_notify(date)
        self.assertEqual(financials.current_date, date)
        self.assertEqual(observer.message, "Renewing berth on 8 for 7 days (700 Cr).")
        self.assertEqual(observer.priority, "")

        date = DateMock(16)
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

        self.assertEqual(financials.salary_paid, DateMock(1))

        date = DateMock(30)
        financials._salary_notification(date)
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(financials.salary_paid, DateMock(29))
        self.assertEqual(observer.message, "Paying crew salaries on 29 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = DateMock(60)
        financials._salary_notification(date)
        self.assertEqual(financials.balance, Credits(98))
        self.assertEqual(financials.salary_paid, DateMock(57))
        self.assertEqual(observer.message, "Paying crew salaries on 57 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = DateMock(120)
        financials._salary_notification(date)
        self.assertEqual(financials.balance, Credits(96))
        self.assertEqual(financials.salary_paid, DateMock(113))
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

        self.assertEqual(financials.loan_paid, DateMock(1))

        date = DateMock(30)
        financials._loan_notification(date)
        self.assertEqual(financials.balance, Credits(99))
        self.assertEqual(financials.loan_paid, DateMock(29))
        self.assertEqual(observer.message, "Paying ship loan on 29 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = DateMock(60)
        financials._loan_notification(date)
        self.assertEqual(financials.balance, Credits(98))
        self.assertEqual(financials.loan_paid, DateMock(57))
        self.assertEqual(observer.message, "Paying ship loan on 57 for 1 Cr.")
        self.assertEqual(observer.priority, "")

        date = DateMock(120)
        financials._loan_notification(date)
        self.assertEqual(financials.balance, Credits(96))
        self.assertEqual(financials.loan_paid, DateMock(113))
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

        self.assertEqual(financials.last_maintenance, DateMock(-13))

        date = DateMock(30)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        date = DateMock(296)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        date = DateMock(297)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "Days since last maintenance = 310")
        self.assertEqual(observer.priority, "yellow")

        date = DateMock(352)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "Days since last maintenance = 365")
        self.assertEqual(observer.priority, "yellow")

        date = DateMock(353)
        financials._maintenance_notification(date)
        self.assertEqual(observer.message, "Days since last maintenance = 366")
        self.assertEqual(observer.priority, "red")

    def test_maintenance_status(self) -> None:
        """Test maintenance status notification."""
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.last_maintenance, DateMock(-13))

        date = DateMock(30)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "green")

        date = DateMock(296)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "green")

        date = DateMock(297)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "yellow")

        date = DateMock(352)
        result = financials.maintenance_status(date)
        self.assertEqual(result, "yellow")

        date = DateMock(353)
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
                         DateMock(1))
        self.assertEqual(financials.current_date,
                         DateMock(1))

        financials.berthing_fee(False)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 6)
        self.assertEqual(financials.berth_expiry,
                         DateMock(1))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        financials.berthing_fee(True)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         DateMock(7))
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
                         DateMock(1))
        self.assertEqual(financials.current_date,
                         DateMock(1))

        date = DateMock(7)
        financials.location.on_surface = lambda : False
        financials._berth_notification(date)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 6)
        self.assertEqual(financials.berth_expiry,
                         DateMock(1))
        self.assertEqual(financials.current_date,
                         DateMock(1))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        financials.location.on_surface = lambda : True
        financials.berth_recurrence = 1
        financials.berth_expiry = financials.current_date + 6
        date = DateMock(8)
        financials._berth_notification(date)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         DateMock(9))
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
                         DateMock(1))
        self.assertEqual(financials.current_date,
                         DateMock(1))

        financials.berth_recurrence = 1
        financials.berth_expiry = financials.current_date + 6
        date = DateMock(7)
        financials._renew_berth(date)
        self.assertEqual(financials.balance, Credits(100))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         DateMock(7))
        self.assertEqual(observer.message, "")
        self.assertEqual(observer.priority, "")

        date = DateMock(8)
        financials._renew_berth(date)
        self.assertEqual(financials.balance, Credits(0))
        self.assertEqual(financials.berth_recurrence, 1)
        self.assertEqual(financials.berth_expiry,
                         DateMock(9))
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

        date = DateMock(2)
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

        string = "100 - 010-1105 - 010-1105 - 010-1105 - 010-1105 - 011-1105"
        with self.assertRaises(ValueError) as context:
            _ = financials_from(string)
        self.assertEqual(f"{context.exception}",
                         "last maintenance value cannot be later than the current date: '011-1105'")

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
