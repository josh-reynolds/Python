"""Contains the DownportScreen class.

DownportScreen - contains commands for the downport state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.starport import StarportScreen

class DownportScreen(StarportScreen):
    """Contains commands for the downport state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a DownportScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('liftoff', 'Lift off to orbit', self.to_orbit),
                Command('depot', 'Trade depot', self.to_depot),
                Command('terminal', 'Passenger terminal', self.to_terminal),
                Command('wilderness', 'Fly to the wilderness', self.to_wilderness),
                ]

        if self.model.has_highport():
            self.commands += [
                Command('highport', 'Lift off to the highport', self.to_highport),
                ]

        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Downport({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def to_orbit(self) -> None:
        """Move from the starport to orbit."""
        print(f"{BOLD_BLUE}Lifting off to orbit {self.model.system_name()}.{END_FORMAT}")
        try:
            print(self.model.liftoff())
            self.parent.change_state("Orbit")
        except GuardClauseFailure as exception:
            print(exception)

    def to_highport(self) -> None:
        """Move from the starport to the highport."""
        print(f"{BOLD_BLUE}Lifting off to dock with the {self.model.system_name()} " +
              f"highport.{END_FORMAT}")
        try:
            print(self.model.dock())
            self.parent.change_state("Highport")
        except GuardClauseFailure as exception:
            print(exception)

    def to_depot(self) -> None:
        """Move from the starport to the trade depot."""
        print(f"{BOLD_BLUE}Entering {self.model.system_name()} trade depot.{END_FORMAT}")
        print(self.model.to_depot())
        self.parent.change_state("Trade")

    def to_terminal(self) -> None:
        """Move from the starport to the passenger terminal."""
        print(f"{BOLD_BLUE}Entering {self.model.system_name()} " +
              f"passenger terminal.{END_FORMAT}")
        print(self.model.to_terminal())
        self.parent.change_state("Terminal")

    # TO_DO: duplicates OrbitScreen.wilderness()
    # pylint: disable=R0801
    # R0801: Similar lines in 2 files
    def to_wilderness(self) -> None:
        """Fly from the starport to the wilderness."""
        print(f"{BOLD_BLUE}Flying to the wilderness on {self.model.system_name()}.{END_FORMAT}")
        try:
            print(self.model.wilderness())
            self.parent.change_state("Wilderness")
        except GuardClauseFailure as exception:
            print(exception)

    # ACTIONS ==============================================================
