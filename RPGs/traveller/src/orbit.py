"""Contains the OrbitScreen class.

OrbitScreen - contains commands for the orbit state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen

class OrbitScreen(PlayScreen):
    """Contains commands for the orbit state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create an OrbitScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('starport', 'Land at the starport', self.to_downport),
                Command('wilderness', 'Land in the wilderness', self.to_wilderness),
                Command('outbound', 'Go to jump point', self.to_jump),
                ]

        if self.model.has_highport():
            self.commands += [
                Command('highport', 'Dock at the highport', self.to_highport),
                    ]

        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Orbit({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # TO_DO: duplicates WildernessScreen.starport()
    # pylint: disable=R0801
    # R0801: Similar lines in 2 files
    def to_downport(self) -> None:
        """Move from orbit to the starport."""
        print(f"{BOLD_BLUE}Landing at the {self.model.system_name()} starport.{END_FORMAT}")
        try:
            print(self.model.land())
            self.parent.change_state("Starport")
        except GuardClauseFailure as exception:
            print(exception)

    def to_highport(self) -> None:
        """Move from orbit to the highport."""
        print(f"{BOLD_BLUE}Docking at the {self.model.system_name()} highport.{END_FORMAT}")
        try:
            print(self.model.dock())
            self.parent.change_state("Highport")
        except GuardClauseFailure as exception:
            print(exception)

    # TO_DO: duplicates StarportScreen.wilderness()
    # pylint: disable=R0801
    # R0801: Similar lines in 2 files
    def to_wilderness(self) -> None:
        """Move from orbit to the wilderness."""
        print(f"{BOLD_BLUE}Landing on {self.model.system_name()}.{END_FORMAT}")
        try:
            print(self.model.wilderness())
            self.parent.change_state("Wilderness")
        except GuardClauseFailure as exception:
            print(exception)

    def to_jump(self) -> None:
        """Move from orbit to the jump point."""
        print(f"{BOLD_BLUE}Travelling out to {self.model.system_name()} jump point.{END_FORMAT}")
        try:
            print(self.model.outbound_to_jump())
            self.parent.change_state("Jump")
        except GuardClauseFailure as exception:
            print(exception)

    # ACTIONS ==============================================================
