"""Contains the StarportScreen class.

StarportScreen - contains commands for the starport state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen

class StarportScreen(PlayScreen):
    """Contains commands for the starport state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a StarportScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('life support', 'Recharge life support', self.recharge),
                Command('refuel', 'Refuel', self.refuel),
                Command('maintenance', 'Annual maintenance', self.maintenance),
                Command('flush tanks', 'Flush fuel tanks', self.flush),
                Command('repair', 'Repair ship', self.repair_ship),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Starport({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        self.model.recharge_life_support()

    def refuel(self) -> None:
        """Refuel the Ship."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        try:
            print(self.model.refuel())
        except GuardClauseFailure as exception:
            print(exception)

    def maintenance(self) -> None:
        """Perform annual maintenance on the Ship."""
        print(f"{BOLD_BLUE}Performing annual ship maintenance.{END_FORMAT}")
        try:
            print(self.model.annual_maintenance())
        except GuardClauseFailure as exception:
            print(exception)

    def flush(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        print(f"{BOLD_BLUE}Flushing out fuel tanks.{END_FORMAT}")
        print(self.model.flush())

    def repair_ship(self) -> None:
        """Fully repair damage to the Ship (Starport)."""
        print(f"{BOLD_BLUE}Starport repairs.{END_FORMAT}")
        print(self.model.repair_ship())
