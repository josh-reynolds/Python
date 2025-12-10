"""Contains the game simulation model with references to all component objects.

Model - contains references to all game model objects.
"""
from src.calendar import Calendar
from src.cargo_depot import CargoDepot
from src.financials import Financials
from src.ship import Ship, RepairStatus
from src.star_system import StarSystem
from src.star_map import StarMap

# pylint: disable=R0903
# R0903: Too few public methods (0/2)
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
