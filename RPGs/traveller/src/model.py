"""Contains the game simulation model with references to all component objects.

Model - contains references to all game model objects.
"""
from typing import List
from src.calendar import Calendar
from src.cargo_depot import CargoDepot
from src.financials import Financials
from src.passengers import Passenger
from src.ship import Ship, RepairStatus, FuelQuality
from src.star_system import StarSystem
from src.star_map import StarMap
from src.utilities import die_roll

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

    def can_travel(self) -> bool:
        """Test whether the Ship can travel to a destination."""
        return self.ship.repair_status != RepairStatus.BROKEN

    def can_jump(self) -> bool:
        """Test whether the Ship can perform a hyperspace jump."""
        return self.ship.repair_status not in (RepairStatus.BROKEN, RepairStatus.PATCHED)

    def can_flush(self) -> bool:
        """Test whether facilities to flush fuel tanks are present at the current location."""
        return self.location.starport in ('A', 'B', 'C', 'D')

    def no_shipyard(self) -> bool:
        """Test whether maintenance can be performed at the current location."""
        return self.location.starport not in ('A', 'B')

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
        if self.location.starport in ["D", "E", "X"]:
            return f"No repair facilities available at starport {self.location.starport}"

        if self.ship.repair_status == RepairStatus.REPAIRED:
            return "Your ship is not damaged."

        self.ship.repair_status = RepairStatus.REPAIRED
        self.ship.fuel_quality = FuelQuality.REFINED
        self.ship.unrefined_jump_counter = 0
        self.date.plus_week()
        return "Your ship is fully repaired and decontaminated."

    def refuel(self) -> str:
        """Refuel the Ship."""
        if self.location.starport in ('E', 'X'):
            return f"No fuel is available at starport {self.location.starport}."

        cost = self.ship.refuel(self.location.starport)
        self.financials.debit(cost, "refuelling")
        return "Your ship is fully refuelled."

    def get_repair_string(self) -> str:
        """Return a string representing current repair state of the Ship."""
        match self.ship.repair_status:
            case RepairStatus.BROKEN:
                return "\tDRIVE FAILURE - UNABLE TO JUMP OR MANEUVER"
            case RepairStatus.PATCHED:
                return "\tSEEK REPAIRS - UNABLE TO JUMP"
            case RepairStatus.REPAIRED:
                return ""

    def set_location(self, location: str) -> None:
        """Set the Model to the specified location."""
        self.location.detail = location

    def system_name(self) -> str:
        """Return the name of the current StarSystem."""
        return self.location.name

    def get_passengers(self) -> List[Passenger]:
        """Return a list of Passengers on board the Ship."""
        return self.ship.passengers

    def set_passengers(self, passengers: List[Passenger]) -> None:
        """Set the list of Passengers on board the Ship."""
        self.ship.passengers = passengers

    def add_passengers(self, passengers: List[Passenger]) -> None:
        """Add a list of Passengers to those present on board the Ship."""
        self.ship.passengers += passengers

    def add_day(self) -> None:
        """Advance the Calendar by a day."""
        self.date.day += 1

    def starport(self) -> str:
        """Return the classification of the current location's starport."""
        return self.location.starport
