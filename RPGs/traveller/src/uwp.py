"""Contains the UWP class and a factory function.

UWP - represents a Traveller Universal World Profile.
uwp_from() - create a UWP object from a string representation.
"""
from typing import Any

# pylint: disable=R0902
# R0902: Too many instance attributes (8/7)
class UWP:
    """Represents a Traveller Universal World Profile."""

    # pylint: disable=R0913
    # R0902: Too many arguments (9/5)
    def __init__(self, starport: str, size: int, atmosphere: int, hydrographics: int,
                 population: int, government: int, law: int, tech: int) -> None:
        """Create an instance of a UWP object."""
        self.starport = starport
        self.size = size
        self.atmosphere = atmosphere
        self.hydrographics = hydrographics
        self.population = population
        self.government = government
        self.law = law
        self.tech = tech

    def __repr__(self) -> str:
        """Return the string representation of a UWP object."""
        return f"UWP({self.starport}, {self.size}, {self.atmosphere}, {self.hydrographics}, " +\
               f"{self.population}, {self.government}, {self.law}, {self.tech})"

    # Check if '77 can generate any values above 15 (F). It's certainly
    # possible in later editions, not sure here...
    # If so, a simple method that indexes a string would work.
    #    chars = "01234567890ABCDEFGHJKLMNPQRSTUVWXYZ"    # omit 'I' and 'O'
    #    e_hex = chars[value]
    def __str__(self) -> str:
        """Return a formatted string for a given UWP.

        Traveller uses a modified hex digit to enforce single digits for 
        all values. They allow values above 15 by extending with the remaining
        alphabet, excluding 'I' and 'O' to avoid confusion with '1' and '0'.

        The current implementation below only allows for values up to 15 to
        display correctly, as the 'e-hex' concept was introduced in a later
        edition of the rules than we're using here.
        """
        return  f"{self.starport}{self.size:X}{self.atmosphere:X}" +\
                f"{self.hydrographics:X}{self.population:X}{self.government:X}" +\
                f"{self.law:X}-{self.tech:X}"

    def __eq__(self, other: Any) -> bool:
        """Test equality for UWPs."""
        if type(other) is type(self):
            return self.starport == other.starport and\
                    self.size == other.size and\
                    self.atmosphere == other.atmosphere and\
                    self.hydrographics == other.hydrographics and\
                    self.population == other.population and\
                    self.government == other.government and\
                    self.law == other.law and\
                    self.tech == other.tech
        return NotImplemented

def uwp_from(string: str) -> UWP:
    """Create a UWP object from a string representation.

    String format matches UWP.__str__ : wdddddd-d
    Digits are hexadecimal values.
    """
    chars = list(string)

    if chars[0] not in ['A', 'B', 'C', 'D', 'E', 'X']:
        raise ValueError(f"invalid literal for starport: '{chars[0]}'")

    if len(chars) != 9:
        raise ValueError(f"string length should be exactly 9 characters: {len(chars)}")

    if chars[7] != '-':
        raise ValueError(f"tech level should be separated by a '-' character: '{chars[7]}'")

    args = [chars[0]] + [int(a, 16) for a in chars[1:7]] + [int(chars[8], 16)]

    # we enforced types above, but mypy is unaware and needs silencing
    return UWP(args[0], args[1], args[2], args[3],        # type: ignore[arg-type]
               args[4], args[5], args[6], args[7])        # type: ignore[arg-type]
