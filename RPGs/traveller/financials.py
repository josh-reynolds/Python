"""Contains classes to handle financial transactions.

Credits - represents units of money.
Financials - contains methods to handle financial
             transactions and track a balance.
"""

class Credits:
    """Represents units of money."""

    def __init__(self, amount):
        """Create an instance of Credits."""
        # should we block negative or zero credits?
        # unsure... what if credits can represent a
        # balance or a debt, not just a pile of cash?
        self.amount = amount

    def __repr__(self):
        """Return the string representation of a Credits object."""
        val = round(self.amount)
        suffix = "Cr"
        if val >= 1000000:
            suffix = "MCr"
            val = val/1000000
        return f"{val:,} {suffix}"

    def __eq__(self, other):
        """Test whether two Credits are equal."""
        if type(other) is type(self):
            return self.amount == other.amount
        return NotImplemented

    def __gt__(self, other):
        """Test whether one Credits object is greater than another."""
        if type(other) is type(self):
            return self.amount > other.amount
        return NotImplemented

    def __ge__(self, other):
        """Test whether one Credits object is greater than or equal to another."""
        if type(other) is type(self):
            return self.amount >= other.amount
        return NotImplemented

    def __add__(self, other):
        """Add together two Credits objects and return a new object."""
        if type(other) is type(self):
            return Credits(self.amount + other.amount)
        return NotImplemented

    def __sub__(self, other):
        """Subtract one Credits object from another and return a new object."""
        if type(other) is type(self):
            return Credits(self.amount - other.amount)
        return NotImplemented

    def __mul__(self, scalar):
        """Multiply Credits by a number and return a new object."""
        if type(scalar) in (int, float):
            return Credits(round(self.amount * scalar))
        return NotImplemented

    def __truediv__(self, scalar):
        """Divide Credits by a number and return a new object.

        Note that fractional Credits are not supported, so this method
        rounds its results.
        """
        if type(scalar) in (int, float):
            return Credits(round(self.amount / scalar))
        return NotImplemented

    def __floordiv__(self, scalar):
        """Divide Credits by an integer and return a new object.

        Note that fractional Credits are not supported, so this method
        rounds its results.
        """
        if type(scalar) is int:
            return Credits(round(self.amount / scalar))
        return NotImplemented

class Financials:
    """Contains methods to handle financial transactions and track a balance."""

    def __init__(self, balance, current_date, ship, location):
        """Create an instance of a Financials object."""
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

        self.observers = []

    def add_observer(self, observer):
        """Add an observer to respond to UI messages."""
        self.observers.append(observer)

    def message_observers(self, message, priority=""):
        for observer in self.observers:
            observer.on_notify(message, priority)

    def debit(self, amount):
        """Deduct a specified amount from the Financials balance."""
        self.balance -= amount

    def credit(self, amount):
        """Add the specified amount to the Financials balance."""
        self.balance += amount

    def on_notify(self, date):
        """On notification from Calendar, check recurring payments.""" 
        self.current_date = date.copy()

        self._berth_notification(date)
        self._salary_notification(date)
        self._loan_notification(date)
        self._maintenance_notification(date)

    def _berth_notification(self, date):
        """Pay recurring fee for starport berth."""
        if date > self.berth_expiry and self.location.on_surface():
            self._renew_berth(date)

    def _salary_notification(self, date):
        """Pay ship's crew monthly salary."""
        duration = (date - self.salary_paid) // self.salary_recurrence
        for _ in range(duration):
            self.salary_paid += self.salary_recurrence
            self._pay_salaries()

    def _loan_notification(self, date):
        """Pay monthly ship loan."""
        duration = (date - self.loan_paid) // self.loan_recurrence
        for _ in range(duration):
            self.loan_paid += self.loan_recurrence
            self._pay_loan()

    def _maintenance_notification(self, date):
        """Check days since last maintenance."""
        status = self.maintenance_status(date)
        if status != 'green':
            self.message_observers(f"Days since last maintenance = {date - self.last_maintenance}",
                                   status)

    # Book 2 p. 7:
    # Average cost is CR 100 to land and remain for up to six days;
    # thereafter, a CR 100 per day fee is imposed for each
    # additional day spent in port. In some locations this fee will
    # be higher, while at others local government subsidies will
    # lower or eliminate it.
    def berthing_fee(self, on_surface):
        """Deduct fee for berth at a starport from Financials balance."""
        if on_surface:
            self.message_observers("Charging 100 Cr berthing fee.")
            self.debit(Credits(100))
            self.berth_recurrence = 1
            self.berth_expiry = self.current_date + 6

    def _renew_berth(self, date):
        """Deduct renewal fee for starport berth from Financials balance."""
        days_extra = date - self.berth_expiry
        if days_extra > 0:
            if days_extra == 1:
                unit = "day"
            else:
                unit = "days"
            amount = Credits(days_extra * 100)
            self.message_observers(f"Renewing berth on {date} for {days_extra} {unit} ({amount}).")
            self.debit(amount)
            self.berth_expiry = date + self.berth_recurrence

    def _pay_salaries(self):
        """Deduct ship salaries from Financials balance."""
        amount = self.ship.crew_salary()
        self.message_observers(f"Paying crew salaries on {self.salary_paid} for {amount}.")
        self.debit(amount)

    def _pay_loan(self):
        """Deduct loan payment from Financials balance."""
        amount = self.ship.loan_payment()
        self.message_observers(f"Paying ship loan on {self.loan_paid} for {amount}.")
        self.debit(amount)

    # conceivably an enum or the like would be better, but
    # we'll stick to simple strings for now...
    def maintenance_status(self, date):
        """Calculate maintenance green/yellow/red status based on days elapsed."""
        amount = date - self.last_maintenance
        if amount <= 365 - (2*28):     # 10 months
            return "green"
        if amount <= 365:            # 12 months
            return "yellow"
        return "red"
