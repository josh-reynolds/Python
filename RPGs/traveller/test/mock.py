"""Contains mock classes for testing."""
from typing import Any, Self, List, cast
from src.calendar import Calendar
from src.cargo import Cargo
from src.cargo_depot import CargoDepot
from src.coordinate import Coordinate
from src.credits import Credits
from src.financials import Financials
from src.freight import Freight
from src.imperial_date import ImperialDate
from src.passengers import Passenger, Passage
from src.ship import Ship
from src.star_system import StarSystem, DeepSpace

class CalendarMock(Calendar):
    """Mocks a Calendar for testing."""

    def __init__(self) -> None:
        """Create an instance of a CalendarMock."""
        super().__init__()


class CargoDepotMock(CargoDepot):
    """Mocks a CargoDepot for testing."""

    def __init__(self) -> None:
        """Create an instance of a CargoDepotMock."""
        super().__init__(SystemMock(), DateMock(1))

class FinancialsMock(Financials):
    """Mocks a Financials for testing."""

    def __init__(self) -> None:
        """Create an instance of a FinancialsMock."""
        super().__init__(1, DateMock(1), ShipMock(), SystemMock())


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
        self.name = name
        self.coordinate = Coordinate(1,1,1)
        self.destinations = []
        self.uwp = 7777777         #type: ignore[assignment]
        self.gas_giant = True
        self.location = "jump"
        self._starport = "A"
        self._hydrographics = 7

    @property
    def hydrographics(self) -> int:
        """Return an overriden UWP hydrographics value."""
        return self._hydrographics

    @property
    def starport(self) -> str:
        """Return an overriden UWP starport value."""
        return self._starport

    @property
    def population(self) -> int:
        """Return an overriden UWP population value."""
        return 5

    @property
    def poor(self) -> bool:
        """Return an overriden Poor trade classification."""
        return True

    @property
    def rich(self) -> bool:
        """Return an overriden Rich trade classification."""
        return True

    @property
    def nonindustrial(self) -> bool:
        """Return an overriden Nonindustrial trade classification."""
        return True

    @property
    def industrial(self) -> bool:
        """Return an overriden Industrial trade classification."""
        return True

    @property
    def nonagricultural(self) -> bool:
        """Return an overriden Nonagricultural trade classification."""
        return True

    @property
    def agricultural(self) -> bool:
        """Return an overriden Agricultural trade classification."""
        return True

    def __str__(self) -> str:
        """Return the string representation of a SystemMock object."""
        return f"{self.coordinate} - {self.name}"

    def __repr__(self) -> str:
        """Return the developer string representation of a SystemMock object."""
        return f"SystemMock('{self.name}')"

    def at_starport(self) -> bool:
        """Test whether the player is at the world's starport."""
        return True


class DeepSpaceMock(DeepSpace):
    """Mocks a DeepSpace for testing."""

    def __init__(self) -> None:
        """Create an instance of a DeepSpaceMock."""
        super().__init__(Coordinate(1,1,1))


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

    def __init__(self, model: str="Type A Free Trader") -> None:
        """Create an instance of a ShipMock object."""
        super().__init__(model)
        self.last_maintenance = DateMock(1)

    def crew_salary(self) -> Credits:
        """Return the amount of monthly salary paid to the Ship's crew."""
        return Credits(1)

    def loan_payment(self) -> Credits:
        """Return the amount paid monthly for the Ship's loan."""
        return Credits(1)


# pylint: disable=R0903
# R0903: Too few public methods (0/2)
class FreightMock(Freight):
    """Mocks a freight interface for testing."""

    def __init__(self, destination: Any) -> None:
        """Create an instance of a FreightMock object."""
        super().__init__(1, SystemMock(), destination)


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
