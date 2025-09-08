class Ship:
    # For now we'll use the stats of a standard Free Trader (Book 2 p. 19) as necessary
    def __init__(self):
        self.hold = []
        self.hold_size = 82
        self.fuel_tank = 30
        self.current_fuel = 30

    def cargo_hold(self):
        for i,item in enumerate(self.hold):
            print(f"{i} - {item}")

    def free_space(self):
        taken = sum([cargo.tonnage for cargo in self.hold])
        return self.hold_size - taken

    # for now keep all cargo lots separate, since the may have had different
    # purchase prices, plus it is simpler
    # if this turns out not to matter, or we can handle via a transaction log
    # instead, then we could merge identical cargo types together
    def load_cargo(self, cargo):
        self.hold.append(cargo)

    def unload_cargo(self, cargo, quantity):
        if quantity == cargo.quantity:
            self.hold.remove(cargo)
        else:
            cargo.quantity -= quantity

    # Book 2 p. 43
    # If characters are skilled in bribery or admin, they may apply these
    # as DMs for the sale of goods. In any given transaction, such DMs may
    # be used by only one person.
    def trade_skill(self):
        return 1

    # Book 2 p. 19
    # ...four for the crew: pilot, engineer, medic and steward...
    # Book 2 p. 6
    # Crew members must be paid monthly:
    # Pilot     6000 Cr
    # Engineer  4000 Cr
    # Medic     2000 Cr
    # Steward   3000 Cr
    def crew_salary(self):
        return 15000

    # Book 2 p. 19
    # Base price for the free trader is 37,080,000 Cr

    # Book 2 p. 5
    # After a down payment of 20% of the cash price of the starship
    # is made...
    # Standard terms involve the payment of 1/240th of the cash
    # price each month for 480 months. In effect, interest and
    # bank financing cost a simple 120% of the cash purchase price.
    # The loan is paid off over a period of 40 years.

    # Book 1 p. 22
    # If the ship benefit is received more than once, each additional
    # receipt is considered to represent actual possession of the ship
    # for a ten-year period. The ship is ten years older, and the total
    # payment term is reduced by ten years.
    
    # TO_DO: We should have a full loan payment record and statement
    #        for the player.
    def loan_payment(self):
        return 37080000 / 240
