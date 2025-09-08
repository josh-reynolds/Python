from calendar import ImperialDate

class Credits:
    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        val = round(self.amount)
        suffix = "Cr"
        if val >= 1000000:
            suffix = "MCr"
            val = val/1000000
        return f"{val:,} {suffix}"

    def __gt__(self, other):
        return self.amount > other.amount

    def __add__(self, other):
        return Credits(self.amount + other.amount)

    def __sub__(self, other):
        return Credits(self.amount - other.amount)

class Financials:
    def __init__(self, balance, current_date, ship):
        self.balance = Credits(balance)
        self.current_date = current_date.copy()
        self.ship = ship
        self.berth_expiry = ImperialDate(self.current_date.day + 6, self.current_date.year)
        self.salary_due = ImperialDate(self.current_date.day + 28, self.current_date.year)
        self.loan_due = ImperialDate(self.current_date.day + 28, self.current_date.year)

    def debit(self, amount):
        self.balance -= amount

    def credit(self, amount):
        self.balance += amount

    def notify(self, date):
        self.current_date = date.copy()
        if date > self.berth_expiry and self.location.on_surface():
            self.renew_berth(date)

        if date > self.salary_due:
            self.pay_salaries(date)

        if date > self.loan_due:
            self.pay_loan(date)

    # a bit kludgy, but this should help break the dependency on
    # the global game object
    def add_location(self, location):
        self.location = location

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
            self.berth_expiry = ImperialDate(self.current_date.day + 6, self.current_date.year)

    def renew_berth(self, date):
        days_extra = date - self.berth_expiry
        if days_extra == 1:
            unit = "day"
        else:
            unit = "days"
        print(f"Renewing berth on {date} for {days_extra} {unit}.")
        self.debit(Credits(days_extra * 100))
        self.berth_expiry = ImperialDate(date.day + days_extra, date.year)

    def pay_salaries(self, date):
        amount = Credits(self.ship.crew_salary())
        print(f"Paying crew salaries on {self.salary_due} for {amount}.")
        self.debit(amount)
        self.salary_due = ImperialDate(self.salary_due.day + 28, self.salary_due.year)

    def pay_loan(self, date):
        amount = Credits(self.ship.loan_payment())
        print(f"Paying ship loan on {self.loan_due} for {amount}.")
        self.debit(amount)
        self.loan_due = ImperialDate(self.loan_due.day + 28, self.loan_due.year)
