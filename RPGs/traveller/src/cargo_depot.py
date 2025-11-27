"""Contains the CargoDepot class and utility/factory functions.

CargoDepot - represents a starport cargo depot.
cargo_hold_from() - return the contents of the cargo hold from a list of strings.
"""
from typing import Dict, List, Tuple, cast, Sequence, Mapping, Any
from src.baggage import baggage_from
from src.cargo import Cargo, cargo_from, get_cargo_table
from src.coordinate import Coordinate
from src.credits import Credits
from src.imperial_date import ImperialDate
from src.freight import Freight, freight_from
from src.star_system import StarSystem, Hex
from src.utilities import die_roll, constrain, actual_value

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

        table = get_cargo_table()
        cargo.append(table[roll])

        return cargo

# TO_DO: should we convert to int in the sub-function?
#        keep it all strings in here?
def cargo_hold_from(strings: List[str],
                    systems: Mapping[Coordinate, Hex]) -> Sequence[Freight | Cargo]:
    """Return the contents of the cargo hold from a list of strings."""
    result: List[Freight | Cargo] = []
    destinations = set()
    for line in strings:
        tokens = line.split(' - ')
        if tokens[0] == "Baggage":
            source = tokens[1]
            destination = tokens[2]
            result.append(baggage_from(source, destination, systems))
            destinations.add(destination)

        elif tokens[0] == "Freight":
            quantity = int(tokens[1])
            source = tokens[2]
            destination = tokens[3]
            result.append(freight_from(quantity, source, destination, systems))
            destinations.add(destination)

        elif tokens[0] == "Cargo":
            name = tokens[1]
            quantity = int(tokens[2])
            if tokens[3] == "None":
                source = None
            else:
                source = tokens[3]
            result.append(cargo_from(name, quantity, source, systems))

        else:
            raise ValueError(f"unknown hold content type: '{tokens[0]}'")

        if len(destinations) > 1:
            raise ValueError(f"more than one destination in saved data: '{destinations}'")

    return result
