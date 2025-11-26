"""Contains the Cargo class and a factory function.

Cargo - represents speculative cargo.
cargo_from() - creates a Cargo object from a parsed source string.
get_cargo_table() - retrieve data from the cargo table file.
"""
from typing import Any, Mapping, Dict
from src.coordinate import Coordinate
from src.financials import Credits
from src.star_system import StarSystem, Hex, verify_world
from src.utilities import die_roll, get_lines, dictionary_from

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

    def __eq__(self, other: Any) -> bool:
        """Test if two Cargos are equal."""
        if type(other) is type(self):
            return self.name == other.name and \
                   self.quantity == other.quantity and \
                   self.source_world == other.source_world

        return NotImplemented

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

    def encode(self) -> str:
        """Return a string encoding the Cargo object to save and load state."""
        if self.source_world:
            coord = f"{self.source_world.coordinate}"
        else:
            coord = "None"
        return f"Cargo - {self.name} - {self.quantity} - {coord}"


def cargo_from(name: str, quantity: int, source: None | str,
                 systems: Mapping[Coordinate, Hex]) -> Cargo:
    """Create a Cargo object from a parsed source string.

    Name must match against the application cargo table. The
    source coordinate string is in the format : (d,d,d), all +/- integers.

    The function also needs access to a dictionary of StarSystems, and
    the coordinate must be a key in that dictionary.
    """
    if not isinstance(quantity, int):
        raise ValueError(f"quantity must be an integer: '{quantity}'")

    if quantity < 1:
        raise ValueError(f"quantity must be a positive number: '{quantity}'")

    table = get_cargo_table()

    cargo: None | Cargo = None
    for item in table.values():
        if item.name == name:
            cargo = item
            break
    if not cargo:
        raise ValueError(f"cargo not found in the cargo table: '{name}'")
    cargo.quantity = quantity

    if source:
        cargo.source_world = verify_world(source, systems)

    return cargo

def get_cargo_table() -> Dict[int, Cargo]:
    """Retrieve data from the cargo table."""
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
    return table
