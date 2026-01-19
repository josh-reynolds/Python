"""Contains the JumpScreen class.

JumpScreen - contains commands for the jump state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen

class JumpScreen(PlayScreen):
    """Contains commands for the jump state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a JumpScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('inbound', 'Inbound to orbit', self.to_orbit),
                Command('jump', 'Jump to new system', self.jump),
                Command('damage control', 'Engineering damage control', self.damage_control),
                ]

        if self.model.gas_giant:
            self.commands += [
                Command('skim', 'Skim fuel from gas giant', self.skim),
                    ]

        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Jump({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def to_orbit(self) -> None:
        """Move from the jump point to orbit."""
        print(f"{BOLD_BLUE}Travelling in to orbit {self.model.system_name()}.{END_FORMAT}")
        try:
            print(self.model.inbound_from_jump())
            self.parent.change_state("Orbit")
        except GuardClauseFailure as exception:
            print(exception)

    # ACTIONS ==============================================================
    def jump(self) -> None:
        """Perform a hyperspace jump to another StarSystem."""
        print(f"{BOLD_BLUE}Preparing for jump.{END_FORMAT}")
        try:
            print(self.model.perform_jump())
            self.parent.change_state("Jump")
        except GuardClauseFailure as exception:
            print(exception)

    def skim(self) -> None:
        """Refuel the Ship by skimming from a gas giant planet."""
        print(f"{BOLD_BLUE}Skimming fuel from a gas giant planet.{END_FORMAT}")
        try:
            print(self.model.skim())
        except GuardClauseFailure as exception:
            print(exception)

    def damage_control(self) -> None:
        """Repair damage to the Ship (Engineer)."""
        print(f"{BOLD_BLUE}Ship's engineer repairing damage.{END_FORMAT}")
        print(self.model.damage_control())
