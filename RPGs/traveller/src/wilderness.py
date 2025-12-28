"""Contains the WildernessScreen class.

WildernessScreen - contains commands for the wilderness state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen

class WildernessScreen(PlayScreen):
    """Contains commands for the wilderness state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a WildernessScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('refuel', 'Refuel', self.refuel),
                Command('liftoff', 'Lift off to orbit', self.liftoff),
                Command('starport', 'Fly to starport', self.starport),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Wilderness({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def liftoff(self) -> None:
        """Move from the surface to orbit."""
        print(f"{BOLD_BLUE}Lifting off to orbit {self.model.system_name()}.{END_FORMAT}")
        try:
            print(self.model.to_orbit())
            self.parent.change_state("Orbit")
        except GuardClauseFailure as exception:
            print(exception)

    # TO_DO: duplicates OrbitScreen.starport()
    # pylint: disable=R0801
    # R0801: Similar lines in 2 files
    def starport(self) -> None:
        """Move from the wilderness to the starport."""
        print(f"{BOLD_BLUE}Flying to {self.model.system_name()} starport.{END_FORMAT}")
        try:
            print(self.model.land())
            self.parent.change_state("Starport")
        except GuardClauseFailure as exception:
            print(exception)

    # ACTIONS ==============================================================
    def refuel(self) -> None:
        """Perform wilderness refuelling."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        try:
            print(self.model.wilderness_refuel())
        except GuardClauseFailure as exception:
            print(exception)
