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
                Command('land', 'Land at starport', self.land),
                Command('outbound', 'Go to jump point', self.outbound_to_jump),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Orbit({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def land(self) -> None:
        """Move from orbit to the starport."""
        print(f"{BOLD_BLUE}Landing on {self.model.system_name()}.{END_FORMAT}")
        try:
            print(self.model.land())
            self.parent.change_state("Starport")
        except GuardClauseFailure as exception:
            print(exception)

    def outbound_to_jump(self) -> None:
        """Move from orbit to the jump point."""
        print(f"{BOLD_BLUE}Travelling out to {self.model.system_name()} jump point.{END_FORMAT}")
        try:
            print(self.model.outbound_to_jump())
            self.parent.change_state("Jump")
        except GuardClauseFailure as exception:
            print(exception)

    # ACTIONS ==============================================================
