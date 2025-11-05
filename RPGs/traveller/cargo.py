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
from typing import Dict, List, Tuple, Any, cast, Mapping, Sequence
from calendar import ImperialDate
from coordinate import Coordinate, coordinate_from
from utilities import die_roll, constrain
from utilities import actual_value, get_lines, dictionary_from
from financials import Credits
from star_system import StarSystem, Hex

class PassageClass(Enum):
    """Denotes the class of a Passenger's ticket."""

    HIGH = 0
    MIDDLE = 1
    LOW = 2


class Passenger:
    """Represents a passenger on a ship."""

    def __init__(self, passage: PassageClass, destination: StarSystem) -> None:
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

        self.guess: int | None = None

        self.survived = True

    def __str__(self) -> str:
        """Return a formatted string for a given Passenger."""
        return f"{self.name} to {self.destination.name}"

    def __repr__(self) -> str:
        """Return the developer string representation of a Passenger."""
        return f"Passenger({self.passage!r}, {self.destination!r})"

    def __eq__(self, other: Any) -> bool:
        """Test if two Passengers are equal."""
        if type(other) is type(self):
            return self.passage == other.passage and self.destination == other.destination
        return NotImplemented

    # TO_DO: should be restricted to low passengers only
    def guess_survivors(self, total: int) -> None:
        """Guess the number of low passage survivors."""
        self.guess = randint(0, total)

    def encode(self) -> str:
        """Return a string encoding the Passenger to save and load state."""
        # strip " passage" from the name for encoding
        return f"{self.name[:-8].lower()} - {self.destination.coordinate}"


def passenger_from(string: str, systems: Mapping[Coordinate, Hex]) -> Passenger:
    """Create a Passenger object from a string representation.

    String format is : passage - destination coordinate
    Passage is either 'high,' 'middle,' or 'low.'
    Destination coordinate is (d,d,d), all +/- integers.

    The function also needs access to a dictionary of StarSystems, and
    the coordinate in the string must be a key in that dictionary.
    """
    tokens = string.split(' - ')

    if len(tokens) > 2:
        raise ValueError(f"input string has extra data: '{string}'")

    if len(tokens) < 2:
        raise ValueError(f"input string is missing data: '{string}'")

    passage_str = tokens[0].lower()
    if passage_str == "high":
        passage = PassageClass.HIGH
    elif passage_str == "middle":
        passage = PassageClass.MIDDLE
    elif passage_str =="low":
        passage = PassageClass.LOW
    else:
        raise ValueError(f"unrecognized passage class: '{passage_str}'")

    coordinate = coordinate_from(tokens[1])
    if coordinate in systems:
        destination = systems[coordinate]
    else:
        raise ValueError(f"coordinate not found in systems list: '{coordinate}'")

    return Passenger(passage, cast(StarSystem, destination))


class Freight:
    """Represents bulk freight."""

    def __init__(self, tonnage: int,
                 source_world: StarSystem, destination_world: StarSystem) -> None:
        """Create an instance of a Freight shipment."""
        self.name = "Freight"
        self.tonnage = tonnage
        self.source_world = source_world
        self.destination_world = destination_world

    def __str__(self) -> str:
        """Return a formatted string for a given Freight shipment."""
        if self.tonnage > 1:
            unit = "tons"
        else:
            unit = "ton"
        return f"{self.name} : {self.tonnage} {unit} : " +\
               f"{self.source_world.name} -> {self.destination_world.name}"

    def __repr__(self) -> str:
        """Return the developer string representation of a Freight shipment."""
        return f"Freight({self.tonnage}, {self.source_world!r}, {self.destination_world!r})"

    def __eq__(self, other: Any) -> bool:
        """Test if two Freight objects are equal."""
        if type(other) is type(self):
            return self.tonnage == other.tonnage and self.source_world == other.source_world \
                    and self.destination_world == other.destination_world
        return NotImplemented


def freight_from(tonnage: int, source: str, destination: str,
                 systems: Mapping[Coordinate, Hex]) -> Freight:
    """Create a Freight object from a parsed source string.

    Both coordinate argumensts are in the format : (d,d,d), all +/- integers.

    The function also needs access to a dictionary of StarSystems, and
    the coordinates must be keys in that dictionary.
    """
    source_coordinate = coordinate_from(source)
    if source_coordinate in systems:
        source_world = cast(StarSystem, systems[source_coordinate])
    else:
        raise ValueError(f"coordinate not found in systems list: '{source}'")

    destination_coordinate = coordinate_from(destination)
    if destination_coordinate in systems:
        destination_world = cast(StarSystem, systems[destination_coordinate])
    else:
        raise ValueError(f"coordinate not found in systems list: '{destination}'")

    return Freight(tonnage, source_world, destination_world)


# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Baggage(Freight):
    """Represents passenger baggage."""

    def __init__(self, source_world: StarSystem,
                 destination_world: StarSystem) -> None:
        """Create an instance of Baggage."""
        super().__init__(1, source_world, destination_world)
        self.name = "Baggage"

    def __repr__(self) -> str:
        """Return the string representation of a piece of Baggage."""
        return f"Baggage({self.source_world!r}, {self.destination_world!r})"


# pylint: disable=R0902
# R0902: Too many instance attributes (8/7)
class Cargo:
    """Represents speculative cargo."""

    # pylint: disable=R0913
    # R0913: Too many arguments (8/5)
    def __init__(self,
                 name: str,
                 quantity: str,
                 price: Credits,
                 unit_size: int,
                 purchase_dms: dict[str, int],
                 sale_dms: dict[str, int],
                 source_world: StarSystem | None = None) -> None:
        """Create an instance of Cargo."""
        self.name = name
        self.quantity = self._determine_quantity(quantity)
        self.price = price
        self.unit_size = unit_size
        self.purchase_dms = purchase_dms
        self.sale_dms = sale_dms
        self.source_world = source_world
        self.price_adjustment = 0.0    # purchase price adjustment
                                       # '0.0' indicates not determined yet

    def __repr__(self) -> str:
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
    def tonnage(self) -> int:
        """Return the total tonnage used by this Cargo."""
        return self.quantity * self.unit_size

    def quantity_string(self, quantity: int) -> str:
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

    def _determine_quantity(self, quantity: str) -> int:
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

    RECURRENCE = 7

    def __init__(self, system: StarSystem, refresh_date: ImperialDate) -> None:
        """Create an instance of a CargoDepot."""
        self.system = system
        self.refresh_date = refresh_date.copy()
        self.cargo = self._determine_cargo()
        self.freight: Dict[StarSystem, List] = {}
        self.passengers: Dict[StarSystem, Tuple[int, ...]] = {}
        self.observers: List[Any] = []
        self.controls: Any = None

    def on_notify(self, date: ImperialDate) -> None:
        """On notification from Calendar, refresh available lots."""
        duration = cast(int, (date - self.refresh_date)) // CargoDepot.RECURRENCE
        for _ in range(duration):
            self.refresh_date += CargoDepot.RECURRENCE
        if duration > 0:       # we only need to refresh the cargo once, not repeatedly
            self.cargo = self._determine_cargo()
            self._refresh_freight(cast(List[StarSystem],
                                       self.system.destinations))
            self._refresh_passengers(cast(List[StarSystem],
                                          self.system.destinations))

    def add_observer(self, observer):
        """Add an observer to respond to UI messages."""
        self.observers.append(observer)

    def message_observers(self, message, priority=""):
        """Send message to all observers with indicated priority."""
        for observer in self.observers:
            observer.on_notify(message, priority)

    def get_input(self, constraint, prompt):
        """Request input from controls."""
        return self.controls.get_input(constraint, prompt)

    def _refresh_freight(self, destinations: Sequence[StarSystem]) -> None:
        """Refresh available Freight shipments."""
        self.freight = {}
        for world in destinations:
            self.freight[world] = []
            for _ in range(world.population):
                self.freight[world].append(die_roll() * 5)
            self.freight[world] = sorted(self.freight[world])

    def _refresh_passengers(self, destinations: Sequence[StarSystem]) -> None:
        """Refresh available passengers.

        Updates the object's passengers dictionary with a tuple of passenger 
        counts, indexed by the PassageClass enumeration.
        """
        self.passengers = {}
        for world in destinations:
            origin_counts = self._passenger_origin_table(self.system.population)
            passengers = self._passenger_destination_table(world.population,
                                                          origin_counts)
            self.passengers[world] = passengers

    def _passenger_origin_table(self, population: int) -> Tuple[int, int, int]:
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

    def _passenger_destination_table(self,
                                     population: int,
                                     counts: Tuple[int, int, int]) -> Tuple[int, ...]:
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

    def get_available_freight(self,
                              destinations: Sequence[StarSystem]
                              ) -> tuple[Coordinate | None, list[Any] | None]:
        """Present a list of worlds and Freight shipments for the player to choose from."""
        if not self.freight:
            self._refresh_freight(destinations)

        for i,world in enumerate(destinations):
            self.message_observers(f"{i} - {world}", "green")
            self.message_observers("   " + str(self.freight[world]))
            self.message_observers("")

        destination_number = self.get_input('int', "Enter destination number: ")
        if destination_number >= len(destinations):
            self.message_observers("That is not a valid destination number.")
            return (None, None)
        world = destinations[destination_number]

        return (world.coordinate, self.freight[world].copy())

    def get_available_passengers(self, destinations: Sequence[StarSystem]) -> tuple:
        """Present a list of worlds and Passengers for the player to choose from."""
        if not self.passengers:
            self._refresh_passengers(destinations)

        for i,world in enumerate(destinations):
            self.message_observers(f"{i} - {world}", "green")
            self.message_observers("   " + str(self.passengers[world]))
            self.message_observers("")

        destination_number = self.get_input('int', "Enter destination number: ")
        if destination_number >= len(destinations):
            self.message_observers("That is not a valid destination number.")
            return (None, None)
        world = destinations[destination_number]

        return (world.coordinate, self.passengers[world])

    def _get_price_modifiers(self, cargo: Cargo, transaction_type: str) -> int:
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

    def get_cargo_lot(self, source: List[Cargo], prompt: str) -> Cargo | None:
        """Select a Cargo lot from a list."""
        item_number = self.get_input('int', f"Enter cargo number to {prompt}: ")
        if item_number >= len(source):
            self.message_observers("That is not a valid cargo ID.")
            return None
        return source[item_number]

    def get_cargo_quantity(self, prompt: str, cargo: Cargo) -> None | int:
        """Get a quantify of Cargo from the player to sell or purchase."""
        quantity = self.get_input('int', f"How many would you like to {prompt}? ")
        if quantity > cargo.quantity:
            self.message_observers("There is not enough available. Specify a lower quantity.")
            return None
        if quantity <= 0:
            self.message_observers("Quantity needs to be a positive number.")
            return None
        return quantity

    def invalid_cargo_origin(self, cargo: Cargo) -> bool:
        """Restrict Cargo sale based on world of origin."""
        if cargo.source_world:
            if cargo.source_world == self.system:
                self.message_observers("You cannot resell cargo on "
                                       + "the world where it was purchased.")
                return True
        return False

    def get_broker(self) -> int:
        """Allow player to select a broker for Cargo sales."""
        broker = self.get_input('confirm', "Would you like to hire a broker (y/n)? ")
        broker_skill = 0
        if broker == 'y':
            while broker_skill < 1 or broker_skill > 4:
                broker_skill = self.get_input('int', "What level of broker (1-4)? ")

            broker_confirm = self.get_input('confirm', "This will incur a " +
                                           f"{5 * broker_skill}% fee. " +
                                            "Confirm (y/n)? ")
            if broker_confirm == 'n':
                broker_skill = 0
        return broker_skill

    # TO_DO: this method is still too unwieldy - break it up further
    def determine_price(self, prompt: str,
                        cargo: Cargo, quantity: int,
                        skill: int) -> Credits:
        """Calculate the price of a Cargo transaction."""
        modifier = self._get_price_modifiers(cargo, prompt)

        if prompt == "sale":
            modifier += skill
            roll = constrain((die_roll(2) + modifier), 2, 15)
            price_adjustment = actual_value(roll)
        elif prompt == "purchase":
            if cargo.price_adjustment > 0:
                price_adjustment = cargo.price_adjustment
            else:
                roll = constrain((die_roll(2) + modifier), 2, 15)
                price_adjustment = actual_value(roll)
                if quantity < cargo.quantity:
                    price_adjustment += .01
                cargo.price_adjustment = price_adjustment

        price = Credits(round(cargo.price.amount * price_adjustment * quantity))
        if ((prompt == "sale" and price_adjustment > 1) or
            (prompt == "purchase" and price_adjustment < 1)):
            pr_function = "green"
        elif ((prompt == "sale" and price_adjustment < 1) or
              (prompt == "purchase" and price_adjustment > 1)):
            pr_function = "red"
        else:
            pr_function = ""

        self.message_observers(f"{prompt.capitalize()} price of that quantity is {price}.",
                               pr_function)
        return price

    def insufficient_hold_space(self, cargo: Cargo,
                                quantity: int, free_space: int) -> bool:
        """Check if a given quantity of Cargo will fit in the Ship's hold."""
        if quantity * cargo.unit_size > free_space:
            self.message_observers("That amount will not fit in your hold.")
            self.message_observers(f"You only have {free_space} tons free.")
            return True
        return False

    def insufficient_funds(self, cost: Credits, balance: Credits) -> bool:
        """Check if the player's bank balance has enough funds for a given cost."""
        if cost > balance:
            self.message_observers("You do not have sufficient funds.")
            self.message_observers(f"Your available balance is {balance}.")
            return True
        return False

    def broker_fee(self, broker_skill: int, sale_price: Credits) -> Credits:
        """Calculate a broker's fee for Cargo sale."""
        if broker_skill > 0:
            broker_fee = Credits(round(sale_price.amount * (.05 * broker_skill)))
            self.message_observers(f"Deducting {broker_fee} broker fee for skill {broker_skill}.")
            return broker_fee
        return Credits(0)

    def confirm_transaction(self, prompt: str, cargo: Cargo,
                            quantity: int, price: Credits) -> bool:
        """Confirm a sale or purchase."""
        confirmation = self.get_input('confirm', f"Confirming {prompt} of "
                                     f"{Cargo.quantity_string(cargo, quantity)} of "
                                     f"{cargo.name} for {price} (y/n)? ")
        if confirmation == 'n':
            self.message_observers(f"Cancelling {prompt}.")
            return False
        return True

    # this overlaps with ship.unload_cargo()...
    def remove_cargo(self, source: List, cargo: Cargo, quantity: int) -> None:
        """Remove cargo from a storage location."""
        if cargo in source:
            if quantity >= cargo.quantity:
                source.remove(cargo)
            else:
                cargo.quantity -= quantity

    def _determine_cargo(self) -> List[Cargo]:
        """Randomly determine a Cargo lot."""
        cargo = []

        first = die_roll()
        if self.system.population <= 5:
            first -= 1
        if self.system.population >= 9:
            first += 1
        first = constrain(first, 1, 6)
        first *= 10

        roll = first + die_roll()

        table = {}
        lines = get_lines("./data/cargo.txt")
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
