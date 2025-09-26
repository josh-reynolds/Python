import unittest
from financials import Credits
from utilities import confirm_input

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
        self.destination = None

    def __repr__(self):
        result = f"{self.name} -- {self.model}\n" +\
                 f"{self.hull} tons : {self.acceleration}G : jump-{self.jump_range}\n" +\
                 f"{self.crew} crew, {self.passengers} passenger staterooms, " +\
                 f"{self.low_berths} low berths"
        return result

    def cargo_hold(self):
        return self.hold

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

        amount = self.fuel_tank - self.current_fuel
        price = Credits(amount * 500)
        confirm = confirm_input(f"Purchase {amount} tons of fuel for {price}? ")
        if confirm == 'n':
            return Credits(0)

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

        price = Credits((self.crew + self.passengers) * 2000 +
                         self.low_berths * 100)
        confirm = confirm_input(f"Recharge life support for {price}? ")
        if confirm == 'n':
            return Credits(0)

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
        return Credits(37080000 / 240)

    def maintenance_cost(self):
        return Credits(37080000 * 0.001)

class ShipTestCase(unittest.TestCase):
    class CargoMock:
        def __init__(self, quantity):
            self.quantity = quantity
        @property
        def tonnage(self):
            return self.quantity

    def setUp(self):
        ShipTestCase.ship = Ship()

    def test_ship_string(self):
        self.assertEqual(f"{ShipTestCase.ship}",
                         "Weaselfish -- Type A Free Trader\n"
                         "200 tons : 1G : jump-1\n"
                         "4 crew, 6 passenger staterooms, 20 low berths")

    def test_cargo_hold_reporting(self):
        cargo1 = ShipTestCase.CargoMock(20)
        cargo2 = ShipTestCase.CargoMock(50)
        self.assertEqual(ShipTestCase.ship.cargo_hold(), [])
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(len(ShipTestCase.ship.cargo_hold()), 1)
        self.assertEqual(ShipTestCase.ship.cargo_hold()[0], cargo1)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(len(ShipTestCase.ship.cargo_hold()), 2)
        self.assertEqual(ShipTestCase.ship.cargo_hold()[1], cargo2)

    def test_loading_cargo(self):
        cargo1 = ShipTestCase.CargoMock(1)
        cargo2 = ShipTestCase.CargoMock(1)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        ShipTestCase.ship.load_cargo(cargo1)
        self.assertEqual(ShipTestCase.ship.free_space(), 81)
        ShipTestCase.ship.load_cargo(cargo2)
        self.assertEqual(ShipTestCase.ship.free_space(), 80)
        self.assertEqual(len(ShipTestCase.ship.hold), 2)

    def test_unloading_cargo(self):
        cargo = ShipTestCase.CargoMock(20)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        ShipTestCase.ship.load_cargo(cargo)
        self.assertEqual(ShipTestCase.ship.free_space(), 62)
        self.assertEqual(len(ShipTestCase.ship.hold), 1)
        ShipTestCase.ship.unload_cargo(cargo, 10)
        self.assertEqual(ShipTestCase.ship.free_space(), 72)
        self.assertEqual(len(ShipTestCase.ship.hold), 1)
        ShipTestCase.ship.unload_cargo(cargo, 10)
        self.assertEqual(ShipTestCase.ship.free_space(), 82)
        self.assertEqual(len(ShipTestCase.ship.hold), 0)

    @unittest.skip("test has side effects: input & printing")
    def test_refuel(self):
        self.assertEqual(ShipTestCase.ship.current_fuel, 0)
        cost = ShipTestCase.ship.refuel()
        self.assertEqual(ShipTestCase.ship.current_fuel, 30)
        self.assertEqual(cost, Credits(15000))    # 'yes' case
        cost = ShipTestCase.ship.refuel()
        self.assertEqual(cost, Credits(0))        # full tank case

    @unittest.skip("test has side effects: input & printing")
    def test_recharge(self):
        self.assertEqual(ShipTestCase.ship.life_support_level, 0)
        cost = ShipTestCase.ship.recharge()
        self.assertEqual(ShipTestCase.ship.life_support_level, 100)
        self.assertEqual(cost, Credits(22000))    # 'yes' case
        cost = ShipTestCase.ship.recharge()
        self.assertEqual(cost, Credits(0))        # full life support case

    def test_trade_skill(self):
        self.assertEqual(ShipTestCase.ship.trade_skill(), 1)

    def test_crew_salary(self):
        self.assertEqual(ShipTestCase.ship.crew_salary(), Credits(15000))

    def test_loan_payment(self):
        self.assertEqual(ShipTestCase.ship.loan_payment(), Credits(154500))

    def test_maintenance_cost(self):
        self.assertEqual(ShipTestCase.ship.maintenance_cost(), Credits(37080))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
