"""Contains classes to track payload of a ship.

PassageClass - enum to denote passenger ticket class.
Passenger - represents a passenger on a ship.
Freight - represents bulk freight.
Baggage - represents passenger baggage.
Cargo - represents speculative cargo.
CargoDepot - represents a starport location for loading and
             unloading Passengers, Freight, Cargo and Baggage.
"""
from enum import Enum
from random import randint
from utilities import die_roll, constrain, int_input, confirm_input
from utilities import actual_value, pr_red, pr_green, get_lines, dictionary_from
from financials import Credits

class PassageClass(Enum):
    """Denotes the class of a Passenger's ticket."""

    HIGH = 0
    MIDDLE = 1
    LOW = 2


class Passenger:
    """Represents a passenger on a ship."""

    def __init__(self, passage, destination):
        """Create an instance of a Passenger."""
        if passage == PassageClass.HIGH:
            self.name = "High passage"
            self.ticket_price = Credits(10000)
        if passage == PassageClass.MIDDLE:
            self.name = "Middle passage"
            self.ticket_price = Credits(8000)
        if passage == PassageClass.LOW:
            self.name = "Low passage"
            self.ticket_price = Credits(1000)
        self.passage = passage

        self.destination = destination

        if die_roll(2) < 7:
            self.endurance = -1
        else:
            self.endurance = 0

        self.guess = None

        self.survived = True

    def __str__(self):
        """Return a formatted string for a given Passenger."""
        return f"{self.name} to {self.destination.name}"

    def __repr__(self):
        """Return the string representation of a Passenger."""
        return f"Passenger({self.passage!r}, {self.destination!r})"

    # TO_DO: should be restricted to low passengers only
    def guess_survivors(self, total):
        """Guess the number of low passage survivors."""
        self.guess = randint(0, total)


class Freight:
    """Represents bulk freight."""

    def __init__(self, tonnage, source_world, destination_world):
        """Create an instance of a Freight shipment."""
        self.name = "Freight"
        self.tonnage = tonnage
        self.source_world = source_world
        self.destination_world = destination_world

    def __str__(self):
        """Return a formatted string for a given Freight shipment."""
        if self.tonnage > 1:
            unit = "tons"
        else:
            unit = "ton"
        return f"{self.name} : {self.tonnage} {unit} : " +\
               f"{self.source_world.name} -> {self.destination_world.name}"

    def __repr__(self):
        """Return the string representation of a Freight shipment."""
        return f"Freight({self.tonnage}, {self.source_world}, {self.destination_world})"


class Baggage(Freight):
    """Represents passenger baggage."""

    def __init__(self, source_world, destination_world):
        """Create an instance of Baggage."""
        super().__init__(1, source_world, destination_world)
        self.name = "Baggage"

    def __repr__(self):
        """Return the string representation of a piece of Baggage."""
        return f"Baggage({self.source_world}, {self.destination_world})"


class Cargo:
    """Represents speculative cargo."""

    def __init__(self, name, quantity, price, unit_size,
                 purchase_dms, sale_dms, source_world=None):
        """Create an instance of Cargo."""
        self.name = name
        self.quantity = self._determine_quantity(quantity)
        self.price = price
        self.unit_size = unit_size
        self.purchase_dms = purchase_dms
        self.sale_dms = sale_dms
        self.source_world = source_world
        self.price_adjustment = 0    # purchase price adjustment
                                     # '0' indicates not determined yet

    def __repr__(self):
        """Return the string representation of a Cargo."""
        if self.unit_size == 1:
            unit = "ton"
        else:
            unit = "item"

        result = f"{self.name} - {self.quantity_string(self.quantity)} - {self.price}/{unit}"
        if self.source_world:
            result += f" ({self.source_world.name})"

        return result

    @property
    def tonnage(self):
        """Return the total tonnage used by this Cargo."""
        return self.quantity * self.unit_size

    def quantity_string(self, quantity):
        """Return a string with proper units for a given quantity.

        The quantity parameter allows specifying partial lots out
        of a full cargo.
        """
        string = f"{quantity}"
        if self.unit_size == 1:
            if quantity == 1:
                string += " ton"
            else:
                string += " tons"
        else:
            string += f" ({self.unit_size} tons/item)"
        return string

    def _determine_quantity(self, quantity):
        """Convert a die roll amount of Cargo to a specific amount.

        If the quantity parameter string contains "Dx" then it
        specifies a random quantity to be generated. Otherwise
        it is an exact amount.
        The value returned is either tonnage or a number of items
        as indicated by the Cargo unit_size field.
        """
        amount = str(quantity)
        if "Dx" in amount:
            die_count, multiplier = [int(n) for n in amount.split("Dx")]
            value = 0
            for _ in range(0, die_count):
                value += die_roll()
            value *= multiplier
            return value
        return int(quantity)


class CargoDepot:
    """Represents a starport cargo depot.

    Has methods for buying and selling Cargo, loading and unloading
    Freight, and booking Passengers and their Baggage.
    """

    def __init__(self, system, refresh_date):
        """Create an instance of a CargoDepot."""
        self.system = system
        self.refresh_date = refresh_date.copy()
        self.recurrence = 7
        self.cargo = self._determine_cargo()
        self.freight = {}
        self.passengers = {}

    def notify(self, date):
        """On notification from Calendar, refresh available lots."""
        duration = (date - self.refresh_date) // self.recurrence
        for _ in range(duration):
            self.refresh_date += self.recurrence
        if duration > 0:       # we only need to refresh the cargo once, not repeatedly
            self.cargo = self._determine_cargo()
            self._refresh_freight(self.system.destinations)
            self._refresh_passengers(self.system.destinations)

    def _refresh_freight(self, destinations):
        """Refresh available Freight shipments."""
        self.freight = {}
        for world in destinations:
            self.freight[world] = []
            for _ in range(world.population):
                self.freight[world].append(die_roll() * 5)
            self.freight[world] = sorted(self.freight[world])

    def _refresh_passengers(self, destinations):
        """Refresh available passengers.

        Returns a tuple of passenger counts, indexed by the 
        PassageClass enumeration.
        """
        self.passengers = {}
        for world in destinations:
            origin_counts = self._passenger_origin_table(self.system.population)
            passengers = self._passenger_destination_table(world.population,
                                                          origin_counts)
            self.passengers[world] = passengers

    def _passenger_origin_table(self, population):
        """Return a number of Passengers based on world of origin.

        This data comes from the table on page 7 of Traveller '77
        Book 2. In that text, the table goes up to population 12,
        but the world generation procedure only generates populations
        up to 10, so those entries are omitted here.
        """
        if population < 2:
            result = (0,0,0)
        if population == 2:
            result = (die_roll()-die_roll(),
                      die_roll()-die_roll(),
                      die_roll(3)-die_roll())
        if population == 3:
            result = (die_roll(3)-die_roll(2),
                      die_roll(2)-die_roll(2),
                      die_roll(3)-die_roll())
        if population == 4:
            result = (die_roll(3)-die_roll(3),
                      die_roll(3)-die_roll(3),
                      die_roll(4)-die_roll())
        if population == 5:
            result = (die_roll(3)-die_roll(2),
                      die_roll(3)-die_roll(2),
                      die_roll(4)-die_roll())
        if population in (6, 7):
            result = (die_roll(3)-die_roll(2),
                      die_roll(3)-die_roll(2),
                      die_roll(3))
        if population == 8:
            result = (die_roll(2)-die_roll(),
                      die_roll(3)-die_roll(2),
                      die_roll(4))
        if population > 8:
            result = (die_roll(2)-die_roll(),
                      die_roll(2)-die_roll(),
                      die_roll(4))
        return result

    def _passenger_destination_table(self, population, counts):
        """Adjust a number of Passengers based on destination.

        This data comes from the table on page 7 of Traveller '77
        Book 2. In that text, the table goes up to population 12,
        but the world generation procedure only generates populations
        up to 10, so those entries are omitted here.
        """
        if population < 2:
            return (0,0,0)
        if population == 2:
            modifiers = (-1,-2,-4)
        if population == 3:
            modifiers = (-1,-1,-3)
        if population == 4:
            modifiers = (-1,-1,-2)
        if population == 5:
            modifiers = (0,-1,-1)
        if population == 6:
            modifiers = (0,0,-1)
        if population == 7:
            modifiers = (0,0,0)
        if population == 8:
            modifiers = (1,0,0)
        if population == 9:
            modifiers = (1,1,0)
        if population == 10:
            modifiers = (1,1,2)

        return tuple(constrain(a + b, 0, 40) for a,b in zip(counts,modifiers))

    def get_available_freight(self, destinations):
        """Present a list of worlds and Freight shipments for the player to choose from."""
        if not self.freight:
            self._refresh_freight(destinations)

        for i,world in enumerate(destinations):
            pr_green(f"{i} - {world}")
            print("   ", self.freight[world])
            print()

        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(destinations):
            print("That is not a valid destination number.")
            return (None, None)
        world = destinations[destination_number]

        return (world.coordinate, self.freight[world].copy())

    def get_available_passengers(self, destinations):
        """Present a list of worlds and Passengers for the player to choose from."""
        if not self.passengers:
            self._refresh_passengers(destinations)

        for i,world in enumerate(destinations):
            pr_green(f"{i} - {world}")
            print("   ", self.passengers[world])
            print()

        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(destinations):
            print("That is not a valid destination number.")
            return (None, None)
        world = destinations[destination_number]

        return (world.coordinate, self.passengers[world])

    def _get_price_modifiers(self, cargo, transaction_type):
        """Return sale or purchase die modifers for a given Cargo."""
        if transaction_type == "purchase":
            table = cargo.purchase_dms
        elif transaction_type == "sale":
            table = cargo.sale_dms
        modifier = 0
        if self.system.agricultural:
            modifier += table.get("Ag",0)
        if self.system.nonagricultural:
            modifier += table.get("Na",0)
        if self.system.industrial:
            modifier += table.get("In",0)
        if self.system.nonindustrial:
            modifier += table.get("Ni",0)
        if self.system.rich:
            modifier += table.get("Ri",0)
        if self.system.poor:
            modifier += table.get("Po",0)
        return modifier

    def get_cargo_lot(self, source, prompt):
        """Select a Cargo lot from a list."""
        item_number = int_input(f"Enter cargo number to {prompt}: ")
        if item_number >= len(source):
            print("That is not a valid cargo ID.")
            return (None, None)
        return (item_number, source[item_number])

    def get_cargo_quantity(self, prompt, cargo):
        """Get a quantify of Cargo from the player to sell or purchase."""
        quantity = int_input(f"How many would you like to {prompt}? ")
        if quantity > cargo.quantity:
            print("There is not enough available. Specify a lower quantity.")
            return None
        if quantity <= 0:
            print("Quantity needs to be a positive number.")
            return None
        return quantity

    def invalid_cargo_origin(self, cargo):
        """Restrict Cargo sale based on world of origin."""
        if cargo.source_world:
            if cargo.source_world == self.system:
                print("You cannot resell cargo on the world where it was purchased.")
                return True
        return False

    def get_broker(self):
        """Allow player to select a broker for Cargo sales."""
        broker = confirm_input("Would you like to hire a broker (y/n)? ")
        broker_skill = 0
        if broker == 'y':
            while broker_skill < 1 or broker_skill > 4:
                broker_skill = int_input("What level of broker (1-4)? ")

            broker_confirm = confirm_input( "This will incur a " +
                                           f"{5 * broker_skill}% fee. " +
                                            "Confirm (y/n)? ")
            if broker_confirm == 'n':
                broker_skill = 0
        return broker_skill

    # TO_DO: this method is still too unwieldy - break it up further
    def determine_price(self, prompt, cargo, quantity, broker_skill, trade_skill):
        """Calculate the price of a Cargo transaction."""
        modifier = self._get_price_modifiers(cargo, prompt)

        if prompt == "sale":
            modifier += trade_skill
            modifier += broker_skill
            roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
            price_adjustment = actual_value(roll)
        elif prompt == "purchase":
            if cargo.price_adjustment > 0:
                price_adjustment = cargo.price_adjustment
            else:
                roll = constrain((die_roll() + die_roll() + modifier), 2, 15)
                price_adjustment = actual_value(roll)
                if quantity < cargo.quantity:
                    price_adjustment += .01
                cargo.price_adjustment = price_adjustment

        price = Credits(cargo.price.amount * price_adjustment * quantity)
        if ((prompt == "sale" and price_adjustment > 1) or
            (prompt == "purchase" and price_adjustment < 1)):
            pr_function = pr_green
        elif ((prompt == "sale" and price_adjustment < 1) or
              (prompt == "purchase" and price_adjustment > 1)):
            pr_function = pr_red
        else:
            pr_function = print

        pr_function(f"{prompt.capitalize()} price of that quantity is {price}.")
        return price

    def insufficient_hold_space(self, cargo, quantity, free_space):
        """Check if a given quantity of Cargo will fit in the Ship's hold."""
        if quantity * cargo.unit_size > free_space:
            print("That amount will not fit in your hold.")
            print(f"You only have {free_space} tons free.")
            return True
        return False

    def insufficient_funds(self, cost, balance):
        """Check if the player's bank balance has enough funds for a given cost."""
        if cost > balance:
            print("You do not have sufficient funds.")
            print(f"Your available balance is {balance}.")
            return True
        return False

    def broker_fee(self, broker_skill, sale_price):
        """Calculate a broker's fee for Cargo sale."""
        if broker_skill > 0:
            broker_fee = Credits(sale_price.amount * (.05 * broker_skill))
            print(f"Deducting {broker_fee} broker fee for skill {broker_skill}.")
            return broker_fee
        return Credits(0)

    def confirm_transaction(self, prompt, cargo, quantity, price):
        """Confirm a sale or purchase."""
        confirmation = confirm_input(f"Confirming {prompt} of "
                                     f"{Cargo.quantity_string(cargo, quantity)} of "
                                     f"{cargo.name} for {price} (y/n)? ")
        if confirmation == 'n':
            print(f"Cancelling {prompt}.")
            return False
        return True

    # this overlaps with ship.unload_cargo()...
    def remove_cargo(self, source, cargo, quantity):
        """Remove cargo from a storage location."""
        if cargo in source:
            if quantity >= cargo.quantity:
                source.remove(cargo)
            else:
                cargo.quantity -= quantity

    def _determine_cargo(self):
        """Randomly determine a Cargo lot."""
        cargo = []

        first = die_roll()
        if self.system.population <= 5:
            first -= 1
        if self.system.population >= 9:
            first += 1
        first = constrain(first, 1, 6)
        first *= 10

        second = die_roll()
        roll = first + second

        table = {}
        lines = get_lines("./cargo.txt")
        for line in lines:
            line = line[:-1] # strip final '\n'

            entry = line.split(', ')
            table_key = int(entry[0])
            name = entry[1]
            quantity = entry[2]
            price = Credits(int(entry[3]))
            unit_size = int(entry[4])
            purchase = dictionary_from(entry[5])
            sale = dictionary_from(entry[6])

            table[table_key] = Cargo(name, quantity, price, unit_size, purchase, sale)

        cargo.append(table[roll])
        return cargo
