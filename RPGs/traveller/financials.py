"""Contains classes to handle financial transactions.

Credits - represents units of money.
Financials - contains methods to handle financial
             transactions and track a balance.
"""
from utilities import pr_red, pr_yellow

class Credits:
    """Represents units of money."""

    def __init__(self, amount):
        # should we block negative or zero credits?
        # unsure... what if credits can represent a
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

    def __ge__(self, other):
        if type(other) is type(self):
            return self.amount >= other.amount
        return NotImplemented

    def __add__(self, other):
        if type(other) is type(self):
            return Credits(self.amount + other.amount)
        return NotImplemented

    def __sub__(self, other):
        if type(other) is type(self):
            return Credits(self.amount - other.amount)
        return NotImplemented

    def __mul__(self, scalar):
        if type(scalar) in (int, float):
            return Credits(round(self.amount * scalar))
        return NotImplemented

class Financials:
    """Contains methods to handle financial transactions and track a balance. """

    def __init__(self, balance, current_date, ship, location):
        self.balance = Credits(balance)
        self.current_date = current_date.copy()
        self.ship = ship
        self.location = location

        self.berth_recurrence = None
        self.berth_expiry = self.current_date.copy()

        self.salary_recurrence = 28
        self.salary_paid = self.current_date.copy()

        self.loan_recurrence = 28
        self.loan_paid = self.current_date.copy()

        self.last_maintenance = self.current_date - 14

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
        for _ in range(duration):
            self.salary_paid += self.salary_recurrence
            self.pay_salaries()

    def loan_notification(self, date):
        duration = (date - self.loan_paid) // self.loan_recurrence
        for _ in range(duration):
            self.loan_paid += self.loan_recurrence
            self.pay_loan()

    def maintenance_notification(self, date):
        status = self.maintenance_status(date)
        if status == 'yellow':
            pr_yellow(f"Days since last maintenance = {date - self.last_maintenance}")
        if status == 'red':
            pr_red(f"Days since last maintenance = {date - self.last_maintenance}")

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
            self.berth_recurrence = 1
            self.berth_expiry = self.current_date + 6

    def renew_berth(self, date):
        days_extra = date - self.berth_expiry
        if days_extra > 0:
            if days_extra == 1:
                unit = "day"
            else:
                unit = "days"
            amount = Credits(days_extra * 100)
            print(f"Renewing berth on {date} for {days_extra} {unit} ({amount}).")
            self.debit(amount)
            self.berth_expiry = date + self.berth_recurrence

    def pay_salaries(self):
        amount = self.ship.crew_salary()
        print(f"Paying crew salaries on {self.salary_paid} for {amount}.")
        self.debit(amount)

    def pay_loan(self):
        amount = self.ship.loan_payment()
        print(f"Paying ship loan on {self.loan_paid} for {amount}.")
        self.debit(amount)

    # conceivably an enum or the like would be better, but
    # we'll stick to simple strings for now...
    def maintenance_status(self, date):
        amount = date - self.last_maintenance
        if amount <= 365 - (2*28):     # 10 months
            return "green"
        if amount <= 365:            # 12 months
            return "yellow"
        return "red"
