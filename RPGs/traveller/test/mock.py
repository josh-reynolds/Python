"""Contains mock classes for testing."""
from typing import Any, Self, List
from src.coordinate import Coordinate
from src.credits import Credits
from src.imperial_date import ImperialDate
from src.ship import Ship
from src.star_system import StarSystem

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class ObserverMock:
    """Mocks an observer for testing."""

    def __init__(self) -> None:
        """Create an instance of an ObserverMock."""
        self.message = ""
        self.priority = ""

    def on_notify(self, message: str, priority: str) -> None:
        """Save message and priority for review on notification."""
        self.message = message
        self.priority = priority


class DateMock(ImperialDate):
    """Mocks a date interface for testing."""

    # pylint: disable=W0231
    # W0231: __init__ method from base class 'ImperialDate' is not called
    def __init__(self, value: int) -> None:
        """Create an instance of a DateMock object."""
        self.value = value

    def copy(self) -> Self:
        """Return a copy of a DateMock object."""
        return DateMock(self.value)            #type: ignore[return-value]

    def __add__(self, rhs: int) -> Self:
        """Add a value to a DateMock object."""
        return DateMock(self.value + rhs)      #type: ignore[return-value]

    def __sub__(self, rhs: Self) -> int:
        """Subtract a value from a DateMock object."""
        return self.value - rhs.value

    def __ge__(self, other: Any) -> bool:
        """Test whether another object is greater than or equal to a DateMock."""
        return self.value >= other.value


# pylint: disable=R0903, R0902
# R0903: Too few public methods (1/2)
# R0902: Too many instance attributes (10/7)
class SystemMock(StarSystem):
    """Mocks a system interface for testing."""

    # pylint: disable=W0231
    # W0231: __init__ method from base class 'StarSystem' is not called
    def __init__(self, name: str="Uranus") -> None:
        """Create an instance of a SystemMock object."""
        self.agricultural = True
        self.nonagricultural = True
        self.industrial = True
        self.nonindustrial = True
        self.rich = True
        self.poor = True
        self.name = name
        self.coordinate = Coordinate(1,1,1)
        self.destinations = []
        self.uwp = 7777777         #type: ignore[assignment]
        self.gas_giant = True

    @property
    def population(self) -> int:
        """Return an overriden UWP population value."""
        return 5

    def __str__(self) -> str:
        """Return the string representation of a SystemMock object."""
        return f"{self.coordinate} - {self.name}"

    def __repr__(self) -> str:
        """Return the developer string representation of a SystemMock object."""
        return f"SystemMock('{self.name}')"

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class ControlsMock:
    """Mocks a controller for testing."""

    def __init__(self, commands: List[Any]) -> None:
        """Create an instance of a ControlsMock."""
        self.commands = commands

    def get_input(self, _constraint: str, _prompt: str) -> str:
        """Return the next command in the list."""
        # not safe if we call too many times...
        return self.commands.pop()

class ShipMock(Ship):
    """Mocks a Ship for testing."""

    def __init__(self, model: str) -> None:
        """Create an instance of a ShipMock object."""
        super().__init__(model)
        self.last_maintenance = DateMock(1)

    def crew_salary(self) -> Credits:
        """Return the amount of monthly salary paid to the Ship's crew."""
        return Credits(1)

    def loan_payment(self) -> Credits:
        """Return the amount paid monthly for the Ship's loan."""
        return Credits(1)
