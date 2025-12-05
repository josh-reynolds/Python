"""Contains mock classes for testing."""
from typing import Any, Self, List, cast
from src.cargo import Cargo
from src.coordinate import Coordinate
from src.credits import Credits
from src.imperial_date import ImperialDate
from src.passengers import Passenger, Passage
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
    """Mocks an ImperialDate for testing."""

    def __init__(self, value: int) -> None:
        """Create an instance of a DateMock object."""
        super().__init__(value, value)
        self.value = value

    def copy(self) -> Self:
        """Return a copy of a DateMock object."""
        return DateMock(self.value)            #type: ignore[return-value]

    def __add__(self, rhs: int) -> Self:
        """Add a value to a DateMock object."""
        return DateMock(self.value + rhs)      #type: ignore[return-value]

    def __sub__(self, rhs: Self) -> int:
        """Subtract either a DateMock or an integer from a DateMock."""
        if isinstance(rhs, DateMock):
            return self.value - rhs.value
        if isinstance(rhs, int):
            return DateMock(self.value - rhs)
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        """Test whether another object is greater than or equal to a DateMock."""
        return self.value >= other.value

    def __str__(self) -> str:
        """Return the string representation of a DateMock object."""
        return f"{self.value}"


# pylint: disable=R0903, R0902
# R0902: Too many instance attributes (10/7)
class SystemMock(StarSystem):
    """Mocks a StarSystem for testing."""

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

    def on_surface(self) -> bool:
        """Test whether the player is on the world's surface."""
        return True


# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class ControlsMock:
    """Mocks a controller for testing."""

    def __init__(self, commands: List[Any]) -> None:
        """Create an instance of a ControlsMock."""
        self.commands = commands
        self.invocations = 0

    def get_input(self, _constraint: str, _prompt: str) -> str:
        """Return the next command in the list."""
        # not safe if we call too many times...
        self.invocations += 1
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


# TO_DO: is this class used anywhere?
# pylint: disable=R0903
# R0903: Too few public methods (0/2)
class FreightMock:
    """Mocks a freight interface for testing."""

    def __init__(self, destination: Any) -> None:
        """Create an instance of a FreightMock object."""
        self.destination_world = destination


# pylint: disable=R0903,W0231
# R0903: Too few public methods (1/2)
class CargoMock(Cargo):
    """Mocks a Cargo for testing."""

    def __init__(self, quantity: int) -> None:
        """Create an instance of a CargoMock object."""
        super().__init__("Test", str(quantity), Credits(1), 1, {}, {})


# pylint: disable=R0903,W0231
# R0903: Too few public methods (1/2)
class PassengerMock(Passenger):
    """Mocks a Passenger for testing."""

    def __init__(self, destination: Any) -> None:
        """Create an instance of a PassengerMock object."""
        super().__init__(Passage.MIDDLE, destination)

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class CalendarObserverMock:
    """Mocks an observer interface for testing."""

    def __init__(self) -> None:
        """Create an instance of an CalendarObserverMock."""
        self.paid_date = ImperialDate(365,1104)
        self.count = 0
        self.event_count = 0
        self.recurrence = 1

    def on_notify(self, date: ImperialDate) -> None:
        """On notification from Calendar, track the event."""
        self.count += 1
        duration = cast(int, (date - self.paid_date)) // self.recurrence
        for _ in range(duration):
            self.event_count += 1
            self.paid_date += self.recurrence
