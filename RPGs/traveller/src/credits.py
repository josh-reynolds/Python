"""Contains the Credits class.

Credits - represents units of money.
"""
from __future__ import annotations
from typing import Any

class Credits:
    """Represents units of money."""

    def __init__(self, amount: int) -> None:
        """Create an instance of Credits."""
        # should we block negative or zero credits?
        # unsure... what if credits can represent a
        # balance or a debt, not just a pile of cash?
        self.amount = amount

    def __str__(self) -> str:
        """Return the string representation of a Credits object."""
        val: int | float = round(self.amount)
        suffix = "Cr"
        if val >= 1000000:
            suffix = "MCr"
            val = val/1000000
        return f"{val:,} {suffix}"

    def __repr__(self) -> str:
        """Return the developer string representation of a Credits object."""
        return f"Credits({self.amount})"

    def __eq__(self, other: Any) -> bool:
        """Test whether two Credits are equal."""
        if type(other) is type(self):
            return self.amount == other.amount
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        """Test whether one Credits object is greater than another."""
        if type(other) is type(self):
            return self.amount > other.amount
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        """Test whether one Credits object is greater than or equal to another."""
        if type(other) is type(self):
            return self.amount >= other.amount
        return NotImplemented

    def __add__(self, other: Any) -> Credits:
        """Add together two Credits objects and return a new object."""
        if type(other) is type(self):
            return Credits(self.amount + other.amount)
        return NotImplemented

    def __sub__(self, other: Any) -> Credits:
        """Subtract one Credits object from another and return a new object."""
        if type(other) is type(self):
            return Credits(self.amount - other.amount)
        return NotImplemented

    def __mul__(self, scalar: Any) -> Credits:
        """Multiply Credits by a number and return a new object."""
        if type(scalar) in (int, float):
            return Credits(round(self.amount * scalar))
        return NotImplemented

    def __truediv__(self, scalar: Any) -> Credits:
        """Divide Credits by a number and return a new object.

        Note that fractional Credits are not supported, so this method
        rounds its results.
        """
        if type(scalar) in (int, float):
            return Credits(round(self.amount / scalar))
        return NotImplemented

    def __floordiv__(self, scalar: Any) -> Credits:
        """Divide Credits by an integer and return a new object.

        Note that fractional Credits are not supported, so this method
        rounds its results.
        """
        if isinstance(scalar, int):
            return Credits(round(self.amount / scalar))
        return NotImplemented
