"""Contains the HighportScreen class.

HighportScreen - contains commands for the highport state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen

class HighportScreen(PlayScreen):
    """Contains commands for the highport state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a HighportScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('life support', 'Recharge life support', self.recharge),
                Command('refuel', 'Refuel', self.refuel),
                Command('launch', 'Return to orbit', self.launch),
                Command('starport', 'Land at the downport', self.starport),
                Command('maintenance', 'Annual maintenance', self.maintenance),
                Command('flush tanks', 'Flush fuel tanks', self.flush),
                Command('repair', 'Repair ship', self.repair_ship),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Highport({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # TO_DO: duplicates WildernessScreen.liftoff()
    # pylint: disable=R0801
    # R0801: Similar lines in 2 files
    def launch(self) -> None:
        """Move from the highport to orbit."""
        print(f"{BOLD_BLUE}Launching to orbit {self.model.system_name()}.{END_FORMAT}")
        try:
            print(self.model.to_orbit())
            self.parent.change_state("Orbit")
        except GuardClauseFailure as exception:
            print(exception)

    # TO_DO: duplicates OrbitScreen.starport()
    # pylint: disable=R0801
    # R0801: Similar lines in 2 files
    def starport(self) -> None:
        """Move from the highport to the downport."""
        print(f"{BOLD_BLUE}Landing at {self.model.system_name()} starport.{END_FORMAT}")
        try:
            print(self.model.land())
            self.parent.change_state("Starport")
        except GuardClauseFailure as exception:
            print(exception)

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
