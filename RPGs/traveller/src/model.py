"""Contains the game simulation model with references to all component objects.

Model - contains references to all game model objects.
"""
from typing import List, Any
from src.calendar import Calendar, modify_calendar_from
from src.cargo_depot import CargoDepot
from src.coordinate import Coordinate
from src.credits import Credits
from src.financials import Financials, financials_from
from src.imperial_date import ImperialDate
from src.passengers import Passenger
from src.ship import Ship, RepairStatus, FuelQuality
from src.star_system import StarSystem, Hex, DeepSpace
from src.star_map import StarMap
from src.utilities import die_roll

# pylint: disable=R0904
# R0904: too many public methods (21/20)
class Model:
    """Contains references to all game model objects."""

    def __init__(self) -> None:
        """Create an instance of a Model object."""
        self.date: Calendar
        self.ship: Ship
        self.star_map: StarMap
        self.location: StarSystem
        self.financials: Financials
        self.depot: CargoDepot

    def __repr__(self) -> str:
        """Return the developer string representation of the Model object."""
        return "Model()"

    # PROCEDURES ========================================
    def damage_control(self) -> str:
        """Repair damage to the Ship (Engineer)."""
        if self.ship.repair_status == RepairStatus.REPAIRED:
            return "Your ship is not damaged."

        if self.ship.repair_status == RepairStatus.PATCHED:
            return "Further repairs require starport facilities."

        self.date.day += 1
        if die_roll(2) + self.ship.engineering_skill() > 9:
            self.ship.repair_status = RepairStatus.PATCHED
            return "Ship partially repaired. Visit a starport for further work."
        return "No progress today. Drives are still out of commission."

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self) -> str:
        """Fully repair damage to the Ship (Starport)."""
        if self.starport in ["D", "E", "X"]:
            return f"No repair facilities available at starport {self.starport}"

        if self.ship.repair_status == RepairStatus.REPAIRED:
            return "Your ship is not damaged."

        self.ship.repair_status = RepairStatus.REPAIRED
        self.clean_fuel_tanks()
        self.plus_week()
        return "Your ship is fully repaired and decontaminated."

    def refuel(self) -> str:
        """Refuel the Ship."""
        if self.starport in ('E', 'X'):
            return f"No fuel is available at starport {self.starport}."

        cost = self.ship.refuel(self.starport)
        self.financials.debit(cost, "refuelling")
        return "Your ship is fully refuelled."

    # DEPOT =============================================

    # FINANCIALS ========================================
    @property
    def balance(self) -> Credits:
        """Return current account balance."""
        return self.financials.balance

    def load_financials(self, data: str, observer: Any) -> None:
        """Apply Financials from json data to Financials field."""
        self.financials = financials_from(data)
        self.financials.ship = self.ship
        self.financials.add_observer(observer)
        self.date.add_observer(self.financials)

    # LOCATION ==========================================
    def system_name(self) -> str:
        """Return the name of the current StarSystem."""
        return self.location.name

    @property
    def starport(self) -> str:
        """Return the classification of the current location's starport."""
        return self.location.starport

    def set_location(self, location: str) -> None:
        """Set the Model to the specified location."""
        self.location.detail = location

    def can_flush(self) -> bool:
        """Test whether facilities to flush fuel tanks are present at the current location."""
        return self.starport in ('A', 'B', 'C', 'D')

    def no_shipyard(self) -> bool:
        """Test whether maintenance can be performed at the current location."""
        return self.starport not in ('A', 'B')

    def in_deep_space(self) -> bool:
        """Test whether the Ship is currently in a DeepSpace Hex."""
        return isinstance(self.location, DeepSpace)

    # STAR MAP ==========================================
    def get_system_at_coordinate(self, coord: Coordinate) -> Hex:
        """Return the contents of the specified coordinate, or create it."""
        return self.star_map.get_system_at_coordinate(coord)

    # SHIP ==============================================
    def destination(self) -> StarSystem | None:
        """Return the Ship's contracted destination, if any."""
        return self.ship.destination

    @property
    def destination_name(self) -> str:
        """Return the name of the Ship's destination."""
        if self.ship.destination:
            return self.ship.destination.name
        return "None"

    def check_unrefined_jump(self) -> None:
        """Track hyperspace jumps performed with unrefined fuel."""
        if self.tanks_are_polluted():
            self.ship.unrefined_jump_counter += 1

    def tanks_are_polluted(self) -> bool:
        """Test whether the Ship's fuel tanks have been polluted by unrefined fuel."""
        return self.ship.fuel_quality == FuelQuality.UNREFINED

    def clean_fuel_tanks(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        self.ship.fuel_quality = FuelQuality.REFINED
        self.ship.unrefined_jump_counter = 0

    def burn_fuel(self, amount: int) -> None:
        """Reduce the fuel in the Ship's tanks by the specified amount."""
        self.ship.current_fuel -= amount

    def tanks_are_full(self) -> bool:
        """Test whether the Ship's fuel tanks are full or not."""
        return self.fuel_level() == self.ship.model.fuel_tank

    def fuel_level(self) -> int:
        """Return the current amount of fuel in the Ship's tanks."""
        return self.ship.current_fuel

    def fill_tanks(self, quality: str="refined") -> None:
        """Fill the Ship's fuel tanks to their full capacity."""
        self.ship.current_fuel = self.ship.model.fuel_tank
        if quality == "unrefined":
            self.ship.fuel_quality = FuelQuality.UNREFINED

    def can_maneuver(self) -> bool:
        """Test whether the Ship can travel to a destination."""
        return self.ship.repair_status != RepairStatus.BROKEN

    def can_jump(self) -> bool:
        """Test whether the Ship can perform a hyperspace jump."""
        return self.ship.repair_status not in (RepairStatus.BROKEN, RepairStatus.PATCHED)

    def get_repair_string(self) -> str:
        """Return a string representing current repair state of the Ship."""
        match self.ship.repair_status:
            case RepairStatus.BROKEN:
                return "\tDRIVE FAILURE - UNABLE TO JUMP OR MANEUVER"
            case RepairStatus.PATCHED:
                return "\tSEEK REPAIRS - UNABLE TO JUMP"
            case RepairStatus.REPAIRED:
                return ""

    def get_passengers(self) -> List[Passenger]:
        """Return a list of Passengers on board the Ship."""
        return self.ship.passengers

    def set_passengers(self, passengers: List[Passenger]) -> None:
        """Set the list of Passengers on board the Ship."""
        self.ship.passengers = passengers

    def add_passengers(self, passengers: List[Passenger]) -> None:
        """Add a list of Passengers to those present on board the Ship."""
        self.ship.passengers += passengers

    @property
    def low_passenger_count(self) -> int:
        """Return the number of low passengers on board."""
        return self.ship.low_passenger_count

    # DATE ==============================================
    def get_current_date(self) -> ImperialDate:
        """Return the Calendar's current date."""
        return self.date.current_date

    @property
    def date_string(self) -> str:
        """Return the current date as a string."""
        return f"{self.date}"

    def add_day(self) -> None:
        """Advance the Calendar by a day."""
        self.date.day += 1

    def plus_week(self) -> None:
        """Move the current day forward by seven days."""
        self.date.plus_week()

    def load_calendar(self, data: str) -> None:
        """Apply date from json data to Game calendar field."""
        self.date = Calendar()
        modify_calendar_from(self.date, data)

    def attach_date_observers(self) -> None:
        """Attach observers to Calendar field."""
        self.date.add_observer(self.depot)
        self.date.add_observer(self.financials)
