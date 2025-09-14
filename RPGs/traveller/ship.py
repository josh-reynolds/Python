from financials import Credits
from utilities import confirm_input
from calendar import ImperialDate

class Ship:
    # For now we'll use the stats of a standard Free Trader (Book 2 p. 19) as necessary
    def __init__(self):
        self.name = "Weaselfish"
        self.model = "Type A Free Trader"
        self.hull = 200
        self.crew = 4
        self.passengers = 6
        self.low_berths = 20
        self.acceleration = 1
        self.streamlined = True
        self.hold = []
        self.hold_size = 82
        self.fuel_tank = 30
        self.current_fuel = 0
        self.jump_range = 1
        self.jump_fuel_cost = 20
        self.trip_fuel_cost = 10
        self.life_support_level = 0
        self.last_maintenance = ImperialDate(351,1104)

    def __repr__(self):
        return f"{self.name} -- {self.model}\n" \
               f"{self.hull} tons : {self.acceleration}G : jump-{self.jump_range}\n" \
               f"{self.crew} crew, {self.passengers} passenger staterooms, {self.low_berths} low berths\n" \
               f"Last maintenance: {self.last_maintenance}"

    # can we deprecate? use CargoDepot.print_cargo_list()
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

    # this may be supplanted by CargoDepot.remove_cargo()...
    def unload_cargo(self, cargo, quantity):
        if quantity == cargo.quantity:
            self.hold.remove(cargo)
        else:
            cargo.quantity -= quantity

    # Book 2 pp. 5-6
    # Starship fuel costs 500 Cr per ton (refined) or 100 Cr per ton
    # (unrefined) at most starports.
    # A power plant, to provide power for one trip ... requires fuel
    # in accordance with the formula 10 * Pn, where Pn is the power plant
    # size rating. The formula indicates the amount of fuel in tons, and 
    # all such fuel is consumed in the process of a normal trip.
    # A jump drive requires fuel to make one jump (regardless of jump 
    # number) based on the formula 0.1 * M * Jn, where M equals the mass
    # displacement of the ship and Jn equals the jump number of the drive.
    # Book 2 p. 19
    # Using the type 200 hull, the free trader...
    # Jump drive-A, maneuver drive-A and power plant-A are all installed...
    # giving the starship capability for acceleration of 1G and jump-1.
    # Fuel tankage for 30 tons...

    # From this, trip fuel usage is 10 tons, and jump-1 is 20 tons. The
    # ship empties its tanks every trip.

    # TO_DO: other angles to add later:
    #   * skimming from gas giants (Book 2 p. 35)
    #   * (will need gas giant presence in StarSystem details)
    #   * effects of unrefined fuel (Book 2 p. 4)
    #   * (will need starport class in StarSystem details)
    #   * ship streamlining - needed to land on worlds with atmosphere,
    #       also for skimming (though this version of the rules doesn't
    #       explicitly state that...)
    def refuel(self):
        if self.current_fuel == self.fuel_tank:
            print("Fuel tank is full.")
            return Credits(0)
        else:
            amount = self.fuel_tank - self.current_fuel
            price = Credits(amount * 500)
            confirm = confirm_input(f"Purchase {amount} tons of fuel for {price}? ")
            if confirm == 'n':
                return Credits(0)
            else:
                print(f"Charging {price} for refuelling")
                self.current_fuel += amount
                return price

    # Book 2 p. 6
    # Each stateroom on a starship, occupied or not, involves a constant overhead
    # cost of 2000 Cr per trip made. Each crew member occupies one stateroom; the
    # remainder are available for high or middle passengers. Each low passage
    # berth (cold sleep capsule) involves an overhead cost of 100 Cr per trip.
    #
    # Notes:
    # since the charge is applied regardless of whether the stateroom was occupied,
    # and applies to the whole trip, not smaller segments of time, we really only have
    # 100% and 0%, no capacity in-between. Not sure it makes sense to measure or
    # portray this as percentages. Was considering a method to translate number of
    # staterooms 'used' into an overall ship percentage, but that's really not
    # necessary.
    #
    # Later rulesets differentiate by occupancy, I think. And possibly give time
    # spans for support duration. Need to check. For now, as with other rules 
    # oddities, we'll keep it RAW.
    def recharge(self):
        if self.life_support_level == 100:
            print("Life support is fully charged.")
            return Credits(0)
        else:
            price = Credits((self.crew + self.passengers) * 2000 +
                             self.low_berths * 100)
            confirm = confirm_input(f"Recharge life support for {price}? ")
            if confirm == 'n':
                return Credits(0)
            else:
                print(f"Charging {price} for life support replenishment.")
                self.life_support_level = 100
                return price

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
        return Credits(15000)

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
    #        Also, what happens if the player doesn't have enough funds?
    #        Is this a simple game-over repossesion?
    def loan_payment(self):
        return 37080000 / 240

    def maintenance_cost(self):
        return 37080000 * 0.001
