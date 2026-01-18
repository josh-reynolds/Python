"""Contains the HighportScreen class.

HighportScreen - contains commands for the highport state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.starport import StarportScreen

class HighportScreen(StarportScreen):
    """Contains commands for the highport state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a HighportScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('launch', 'Return to orbit', self.to_orbit),
                Command('starport', 'Land at the downport', self.to_downport),
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
    def to_orbit(self) -> None:
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
    def to_downport(self) -> None:
        """Move from the highport to the downport."""
        print(f"{BOLD_BLUE}Landing at {self.model.system_name()} starport.{END_FORMAT}")
        try:
            print(self.model.land())
            self.parent.change_state("Starport")
        except GuardClauseFailure as exception:
            print(exception)

    # ACTIONS ==============================================================
