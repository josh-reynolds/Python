"""Contains classes representing crew of a starship.

Crew - base class for crewmembers.
Pilot - represents a pilot on board a ship.
Engineer - represents an engineer on board a ship.
Medic - represents a medic on board a ship.
Steward - represents a steward on board a ship.
"""
from abc import ABC, abstractmethod
from src.credits import Credits

# TO_DO: assess collapsing all crew positions into a single class
class Crew(ABC):
    """Base class for crewmembers."""

    def __init__(self, skill: int=1, trade: int=0) -> None:
        """Create an instance of a Crew object."""
        self.name = ""
        self.job = ""
        self.skill = skill
        self.trade_skill = trade

    def __repr__(self) -> str:
        """Return the string representation of a Crew object."""
        return f"{self.name} - {self.job} {self.skill}"

    @abstractmethod
    def salary(self) -> Credits:
        """Return the monthly salary for the crewmember."""


# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Pilot(Crew):
    """Represents a pilot on board a ship."""

    def __init__(self, skill: int=1, trade: int=0) -> None:
        """Create an instance of a Pilot."""
        super().__init__(skill, trade)
        self.name = "Captain Grungebottom"
        self.job = "Pilot"

    def salary(self) -> Credits:
        """Return the monthly salary for a Pilot based on expertise."""
        return Credits(6000) * (1 + .1 * (self.skill - 1))


# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Engineer(Crew):
    """Represents an engineer on board a ship."""

    def __init__(self, skill: int=1, trade: int=0) -> None:
        """Create an instance of an Engineer."""
        super().__init__(skill, trade)
        self.name = "Skins McFlint"
        self.job = "Engineer"

    def salary(self) -> Credits:
        """Return the monthly salary for an Engineer based on expertise."""
        return Credits(4000) * (1 + .1 * (self.skill - 1))


# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Medic(Crew):
    """Represents a medic on board a ship."""

    def __init__(self, skill: int=1, trade: int=0) -> None:
        """Create an instance of a Medic."""
        super().__init__(skill, trade)
        self.name = "Doc Gubbins"
        self.job = "Medic"

    def salary(self) -> Credits:
        """Return the monthly salary for a Medic based on expertise."""
        return Credits(2000) * (1 + .1 * (self.skill - 1))


# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Steward(Crew):
    """Represents a steward on board a ship."""

    def __init__(self, skill: int=1, trade: int=0) -> None:
        """Create an instance of a Steward."""
        super().__init__(skill, trade)
        self.name = "Laszlo the Third"
        self.job = "Steward"

    def salary(self) -> Credits:
        """Return the monthly salary for a Steward based on expertise."""
        return Credits(3000) * (1 + .1 * (self.skill - 1))
