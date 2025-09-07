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
