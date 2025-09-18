import unittest
from utilities import pr_red, pr_yellow

class Credits:
    def __init__(self, amount):
        # should we block negative or zero credits?
        # unsure... what credits can represent a
        # balance or a debt, not just a pile of cash?
        self.amount = amount

    def __repr__(self):
        val = round(self.amount)
        suffix = "Cr"
        if val >= 1000000:
            suffix = "MCr"
            val = val/1000000
        return f"{val:,} {suffix}"

    def __eq__(self, other):
        if type(other) is type(self):
            return self.amount == other.amount
        return NotImplemented

    def __gt__(self, other):
        if type(other) is type(self):
            return self.amount > other.amount
        return NotImplemented

    def __add__(self, other):
        if type(other) is type(self):
            return Credits(self.amount + other.amount)
        return NotImplemented

    def __sub__(self, other):
        if type(other) is type(self):
            return Credits(self.amount - other.amount)
        return NotImplemented

class Financials:
    def __init__(self, balance, current_date, ship, location):
        self.balance = Credits(balance)
        self.current_date = current_date.copy()
        self.ship = ship
        self.location = location

        self.berth_recurrence = 6
        self.berth_expiry = self.current_date + self.berth_recurrence

        self.salary_recurrence = 28
        self.salary_paid = self.current_date.copy()

        self.loan_recurrence = 28
        self.loan_due = self.current_date + self.loan_recurrence

    def debit(self, amount):
        self.balance -= amount

    def credit(self, amount):
        self.balance += amount

    def notify(self, date):
        self.current_date = date.copy()

        self.berth_notification(date)
        self.salary_notification(date)
        self.loan_notification(date)
        self.maintenance_notification(date)

    def berth_notification(self, date):
        if date > self.berth_expiry and self.location.on_surface():
            self.renew_berth(date)

    def salary_notification(self, date):
        duration = (date - self.salary_paid) // self.salary_recurrence
        for i in range(duration):
            self.salary_paid += self.salary_recurrence
            self.pay_salaries()

    def loan_notification(self, date):
        if date > self.loan_due:
            self.pay_loan()

    def maintenance_notification(self, date):
        status = self.maintenance_status(date)
        if status == 'yellow':
            pr_yellow(f"Days since last maintenance = {date - self.ship.last_maintenance}")
        if status == 'red':
            pr_red(f"Days since last maintenance = {date - self.ship.last_maintenance}")

    # Book 2 p. 7:
    # Average cost is CR 100 to land and remain for up to six days;
    # thereafter, a CR 100 per day fee is imposed for each
    # additional day spent in port. In some locations this fee will
    # be higher, while at others local government subsidies will 
    # lower or eliminate it.
    def berthing_fee(self, on_surface):
        if on_surface:
            print("Charging 100 Cr berthing fee.")
            self.debit(Credits(100))
            self.berth_expiry = self.current_date + 6

    def renew_berth(self, date):
        days_extra = date - self.berth_expiry
        if days_extra == 1:
            unit = "day"
        else:
            unit = "days"
        print(f"Renewing berth on {date} for {days_extra} {unit}.")
        self.debit(Credits(days_extra * 100))
        self.berth_expiry = date + 1

    def pay_salaries(self):
        amount = self.ship.crew_salary()
        print(f"Paying crew salaries on {self.salary_paid} for {amount}.")
        self.debit(amount)

    def pay_loan(self):
        amount = self.ship.loan_payment()
        print(f"Paying ship loan on {self.loan_due} for {amount}.")
        self.debit(amount)
        self.loan_due = self.loan_due + 28

    # conceivably an enum or the like would be better, but
    # we'll stick to simple strings for now...
    def maintenance_status(self, date):
        amount = date - self.ship.last_maintenance
        if amount <= 365 - (2*28):     # 10 months
            return "green"
        elif amount <= 365:            # 12 months
            return "yellow"
        else:
            return "red"

class CreditsTestCase(unittest.TestCase):
    def test_credits_string(self):
        a = Credits(1)
        b = Credits(10)
        c = Credits(100)
        d = Credits(1000)
        e = Credits(10000)
        f = Credits(100000)
        g = Credits(1000000)
        h = Credits(11500000)
        i = Credits(1000000000)
        self.assertEqual(f"{a}", "1 Cr")
        self.assertEqual(f"{b}", "10 Cr")
        self.assertEqual(f"{c}", "100 Cr")
        self.assertEqual(f"{d}", "1,000 Cr")
        self.assertEqual(f"{e}", "10,000 Cr")
        self.assertEqual(f"{f}", "100,000 Cr")
        self.assertEqual(f"{g}", "1.0 MCr")
        self.assertEqual(f"{h}", "11.5 MCr")
        self.assertEqual(f"{i}", "1,000.0 MCr")

    def test_credits_comparison(self):
        a = Credits(1)
        b = Credits(2)
        c = Credits(2)
        self.assertGreater(b,a)
        self.assertLess(a,b)
        self.assertEqual(b,c)

    def test_credits_addition(self):
        a = Credits(1)
        b = Credits(1)
        self.assertEqual(a+b,Credits(2))

    def test_credits_subtraction(self):
        a = Credits(1)
        b = Credits(2)
        self.assertEqual(b-a,Credits(1))

class FinancialsTestCase(unittest.TestCase):
    class DateMock:
        def __init__(self, value):
            self.value = value

        def copy(self):
            return FinancialsTestCase.DateMock(self.value)

        def __add__(self, rhs):
            return FinancialsTestCase.DateMock(self.value + rhs)

        def __sub__(self, rhs):
            return self.value - rhs.value

        def __eq__(self, other):
            return self.value == other.value
        
        def __ge__(self, other):
            return self.value >= other.value

        def __gt__(self, other):
            return self.value > other.value

        def __repr__(self):
            return f"{self.value}"

    class ShipMock:
        def __init__(self):
            self.last_maintenance = FinancialsTestCase.DateMock(1)

        def crew_salary(self):
            return Credits(1)

    class SystemMock:
        def on_surface(self):
            return True

    def setUp(self):
        FinancialsTestCase.financials = Financials(100, 
                                                   FinancialsTestCase.DateMock(1),
                                                   FinancialsTestCase.ShipMock(), 
                                                   FinancialsTestCase.SystemMock())

    @unittest.skip("test has side effects: printing")
    def test_notify(self):
        financials = FinancialsTestCase.financials

        date = FinancialsTestCase.DateMock(8)
        financials.notify(date)
        self.assertEqual(financials.current_date, date)

        date = FinancialsTestCase.DateMock(12)
        financials.notify(date)
        self.assertEqual(financials.current_date, date)

    def test_debit_and_credit(self):
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))

        financials.debit(Credits(10))
        self.assertEqual(financials.balance, Credits(90))

        financials.credit(Credits(20))
        self.assertEqual(financials.balance, Credits(110))

    @unittest.skip("test has side effects: printing")
    def test_salary_notification(self):
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

        date = FinancialsTestCase.DateMock(90)
        financials.salary_notification(date)
        self.assertEqual(financials.balance, Credits(97))
        self.assertEqual(financials.salary_paid, FinancialsTestCase.DateMock(85))

    @unittest.skip("test has side effects: printing")
    def test_pay_salaries(self):
        financials = FinancialsTestCase.financials
        self.assertEqual(financials.balance, Credits(100))

        financials.pay_salaries()
        self.assertEqual(financials.balance, Credits(99))


# Observer:paid_date
# Observer:recurrence
# Observer:notify(date)
#    duration = (date - paid_date) // recurrence
#    for i in range(duration):
#      execute_action
#      paid_date += recurrence

    # berth_notification
    # berthing_fee
    # renew_berth

    # loan_notification
    # pay_loan

    # maintenance_notification
    # maintenance_status

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
