"""Contains classes to manage a starship and its crew.

Crew - base class for crewmembers.
Pilot - represents a pilot on board a ship.
Engineer - represents an engineer on board a ship.
Medic - represents a medic on board a ship.
Steward - represents a steward on board a ship.
FuelQuality - enem to represent whether fuel is contaminated or not.
RepairStatus - enum to represent whether a ship needs repairs.
Ship - represents a starship.
"""
from abc import ABC, abstractmethod
from enum import Enum
from cargo import Freight, PassageClass
from financials import Credits
from star_system import StarSystem
from utilities import die_roll

class Crew(ABC):
    """Base class for crewmembers."""

    def __init__(self, skill=1, trade=0):
        """Create an instance of a Crew object."""
        self.skill = skill
        self.trade_skill = trade

    @abstractmethod
    def salary(self):
        """Return the monthly salary for the crewmember."""


class Pilot(Crew):
    """Represents a pilot on board a ship."""

    def __init__(self, skill=1, trade=0):
        """Create an instance of a Pilot."""
        super().__init__(skill, trade)
        self.name = "Captain Grungebottom"

    def __repr__(self):
        """Return the string representation of a Pilot."""
        return f"{self.name} - Pilot {self.skill}"

    def salary(self):
        """Return the monthly salary for a Pilot based on expertise."""
        return Credits(6000) * (1 + .1 * (self.skill - 1))


class Engineer(Crew):
    """Represents an engineer on board a ship."""

    def __init__(self, skill=1, trade=0):
        """Create an instance of an Engineer."""
        super().__init__(skill, trade)
        self.name = "Skins McFlint"

    def __repr__(self):
        """Return the string representation of an Engineer."""
        return f"{self.name} - Engineer {self.skill}"

    def salary(self):
        """Return the monthly salary for an Engineer based on expertise."""
        return Credits(4000) * (1 + .1 * (self.skill - 1))


class Medic(Crew):
    """Represents a medic on board a ship."""

    def __init__(self, skill=1, trade=0):
        """Create an instance of a Medic."""
        super().__init__(skill, trade)
        self.name = "Doc Gubbins"

    def __repr__(self):
        """Return the string representation of a Medic."""
        return f"{self.name} - Medic {self.skill}"

    def salary(self):
        """Return the monthly salary for a Medic based on expertise."""
        return Credits(2000) * (1 + .1 * (self.skill - 1))


class Steward(Crew):
    """Represents a steward on board a ship."""

    def __init__(self, skill=1, trade=0):
        """Create an instance of a Steward."""
        super().__init__(skill, trade)
        self.name = "Laszlo the Third"

    def __repr__(self):
        """Return the string representation of a Steward."""
        return f"{self.name} - Steward {self.skill}"

    def salary(self):
        """Return the monthly salary for a Steward based on expertise."""
        return Credits(3000) * (1 + .1 * (self.skill - 1))


class FuelQuality(Enum):
    """Represents whether fuel is contaminated or not."""

    UNREFINED = 0
    REFINED = 1


class RepairStatus(Enum):
    """Represents whether a ship needs repairs."""

    REPAIRED = 0
    PATCHED = 1
    BROKEN = 2


class Ship:
    """Represents a starship."""

    # For now we'll use the stats of a standard Free Trader (Book 2 p. 19) as necessary
    def __init__(self):
        """Create an instance of a Ship."""
        self.name = "Weaselfish"
        self.model = "Type A Free Trader"
        self.hull = 200
        self.passenger_berths = 6
        self.low_berths = 20
        self.acceleration = 1
        self.streamlined = True
        self.hold = []
        self.hold_size = 82
        self.fuel_tank = 30
        self.fuel = 0
        self.jump_range = 1
        self.jump_fuel_cost = 20
        self.trip_fuel_cost = 10
        self.fuel_quality = FuelQuality.REFINED
        self.unrefined_jump_counter = 0
        self.repair_status = RepairStatus.REPAIRED
        self.life_support_level = 0
        self.passengers = []
        self.crew = [Pilot(), Engineer(), Medic(), Steward(trade=1)]
        self.base_price = Credits(37080000)
        self.observers = []
        self.controls = None

    def __repr__(self):
        """Return the string representation of a Ship."""
        result = f"{self.name} -- {self.model}\n" +\
                 f"{self.hull} tons : {self.acceleration}G : jump-{self.jump_range}\n" +\
                 f"{len(self.crew)} crew, {self.passenger_berths} passenger staterooms, " +\
                 f"{self.low_berths} low berths\n" +\
                 f"Cargo hold {self.hold_size} tons, fuel tank {self.fuel_tank} tons"
        if self.fuel_quality == FuelQuality.UNREFINED:
            result += "\nUnrefined fuel in tanks."

        return result

    @property
    def current_fuel(self):
        """Return the amount of fuel currently in the tanks."""
        return self.fuel

    @current_fuel.setter
    def current_fuel(self, value):
        self.fuel = value

    @property
    def destination(self):
        """Determine Ship's contracted destination based on Freight and Passengers on board."""
        freight_destinations = {f.destination_world for f in self.hold if
                                                            isinstance(f, Freight)}
        freight_count = len(freight_destinations)

        passenger_destinations = {p.destination for p in self.passengers}
        passenger_count = len(passenger_destinations)

        if freight_count > 1 or passenger_count > 1:
            raise ValueError("More than one destination between Freight and Passengers!")

        if freight_count == 0 and passenger_count == 0:
            result = None

        if freight_count == 1 and passenger_count == 0:
            result = freight_destinations.pop()

        if freight_count == 0 and passenger_count == 1:
            result = passenger_destinations.pop()

        if freight_count == 1 and passenger_count == 1:
            freight_destination = freight_destinations.pop()
            passenger_destination = passenger_destinations.pop()
            if freight_destination != passenger_destination:
                raise ValueError("More than one destination between Freight and Passengers!")
            result = freight_destination

        return result

    @property
    def total_passenger_count(self):
        """Return the total number of passengers on board."""
        return self.high_passenger_count +\
                self.middle_passenger_count +\
                self.low_passenger_count
    @property
    def high_passenger_count(self):
        """Return the number of high passengers on board."""
        return sum(1 for passenger in self.passengers if
                   passenger.passage == PassageClass.HIGH)

    @property
    def middle_passenger_count(self):
        """Return the number of middle passengers on board."""
        return sum(1 for passenger in self.passengers if
                    passenger.passage == PassageClass.MIDDLE)

    @property
    def low_passenger_count(self):
        """Return the number of low passengers on board."""
        return sum(1 for passenger in self.passengers if
                    passenger.passage == PassageClass.LOW)

    @property
    def empty_passenger_berths(self):
        """Return the number of unoccupied passenger staterooms."""
        return self.passenger_berths - self.high_passenger_count - self.middle_passenger_count

    @property
    def empty_low_berths(self):
        """Return the number of unoccupied low berths."""
        return self.low_berths - self.low_passenger_count

    def add_observer(self, observer):
        """Add an observer to respond to UI messages."""
        self.observers.append(observer)

    def message_observers(self, message, priority=""):
        """Pass a message on to all observers."""
        for observer in self.observers:
            observer.on_notify(message, priority)

    def get_input(self, constraint, prompt):
        """Request input from controls."""
        return self.controls.get_input(constraint, prompt)

    def cargo_hold(self):
        """Return the contents of the Ship's cargo hold."""
        return self.hold

    def free_space(self):
        """Return the amount of free space in the cargo hold, in displacement tons."""
        taken = sum(cargo.tonnage for cargo in self.hold)
        return self.hold_size - taken

    # for now keep all cargo lots separate, since the may have had different
    # purchase prices, plus it is simpler
    # if this turns out not to matter, or we can handle via a transaction log
    # instead, then we could merge identical cargo types together
    def load_cargo(self, cargo):
        """Load cargo into the Ship's hold."""
        self.hold.append(cargo)

    # this may be supplanted by CargoDepot.remove_cargo()...
    def unload_cargo(self, cargo, quantity):
        """Remove cargo from the Ship's hold."""
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
    def refuel(self, starport):
        """Refuel the Ship, accounting for fuel type."""
        if self.current_fuel == self.fuel_tank:
            self.message_observers("Fuel tank is full.")
            return Credits(0)

        if starport not in ("A", "B"):
            per_ton = 100
            self.message_observers("Note: only unrefined fuel available at this facility.")
        else:
            per_ton = 500

        amount = self.fuel_tank - self.current_fuel
        price = Credits(amount * per_ton)
        confirm = self.get_input('confirm', f"Purchase {amount} tons of fuel for {price}? ")
        if confirm == 'n':
            return Credits(0)

        self.message_observers(f"Charging {price} for refuelling.")
        self.current_fuel += amount
        if starport not in ("A", "B"):
            self.fuel_quality = FuelQuality.UNREFINED
        return price

    def sufficient_jump_fuel(self):
        """Test whether there is enough fuel to make a jump."""
        return self.jump_fuel_cost <= self.current_fuel

    def insufficient_jump_fuel_message(self):
        """Return message for when there is not enough fuel for a jump."""
        return f"Insufficient fuel. Jump requires {self.jump_fuel_cost} tons, only " +\
               f"{self.current_fuel} tons in tanks."

    def sufficient_life_support(self):
        """Test whether there is enough life support for a jump."""
        return self.life_support_level == 100

    def insufficient_life_support_message(self):
        """Return message for when there is not enough life support for a jump."""
        return "Insufficient life support to survive jump.\n" + \
               f"Life support is at {self.life_support_level}%."

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
        """Recharge the Ship's life support system."""
        if self.life_support_level == 100:
            self.message_observers("Life support is fully charged.")
            return Credits(0)

        price = Credits((len(self.crew) + self.passenger_berths) * 2000 +
                         self.low_berths * 100)
        confirm = self.get_input('confirm', f"Recharge life support for {price}? ")
        if confirm == 'n':
            return Credits(0)

        self.message_observers(f"Charging {price} for life support replenishment.")
        self.life_support_level = 100
        return price

    # Book 2 p. 43
    # If characters are skilled in bribery or admin, they may apply these
    # as DMs for the sale of goods. In any given transaction, such DMs may
    # be used by only one person.
    def trade_skill(self):
        """Return the best trade skill from the Ship's crew."""
        return max(c.trade_skill for c in self.crew)

    # Book 2 p. 2 [for low berth survival]
    #   attending medic of expertise 2 or better, +1
    def medic_skill(self):
        """Return the best medic skill from the Ship's crew."""
        skills = [c.skill for c in self.crew if isinstance(c, Medic)]
        if len(skills) > 0:
            if max(skills) > 1:
                return 1
            return 0
        raise ValueError("No medic on board!")

    def engineering_skill(self):
        """Return the best engneering skill from the Ship's crew."""
        skills = [c.skill for c in self.crew if isinstance(c, Engineer)]
        if len(skills) > 0:
            return max(skills)
        raise ValueError("No engineer on board!")

    # Book 2 p. 19
    # ...four for the crew: pilot, engineer, medic and steward...
    # Book 2 p. 6
    # Crew members must be paid monthly:
    # Pilot     6000 Cr
    # Engineer  4000 Cr
    # Medic     2000 Cr
    # Steward   3000 Cr
    #
    # (with suitable modifications for expertise or seniority,
    #  generally +10% for eachlevel of expertise above level-1)
    def crew_salary(self):
        """Return the total monthly salary for the ship's crew."""
        return Credits(sum(c.salary().amount for c in self.crew))

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
        """Return the monthly loan payment amount for the Ship."""
        return self.base_price / 240

    def maintenance_cost(self):
        """Return the annual maintenance cost for the Ship."""
        return self.base_price * 0.001

    def warn_if_not_contracted(self, destination: StarSystem) -> None:
        """Notify the player if they choose a different jump target while under contract."""
        if self.destination is not None and self.destination != destination:
            self.message_observers(f"Warning: your contracted destination is {self.destination.name} " +
                   f"not {destination.name}.", "red")

    def check_failure_pre_jump(self, maintenance_status):
        """Test for drive failure before performing a hyperspace jump."""
        if (maintenance_status == "red" and die_roll(2) == 12):
            self.repair_status = RepairStatus.BROKEN
            self.message_observers("Warning: drive failure! Unable to jump.", "red")

    def check_failure_post_jump(self):
        """Test for drive failure after completing a hyperspace jump."""
        if (self.fuel_quality == FuelQuality.UNREFINED and
            die_roll(2) + self.unrefined_jump_counter > 10):
            self.repair_status = RepairStatus.BROKEN
            self.message_observers("Warning: drive failure!", "red")
