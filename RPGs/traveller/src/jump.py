"""Contains the JumpScreen class.

JumpScreen - contains commands for the jump state.
"""
from typing import Any, cast
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.model import Model
from src.play import PlayScreen
from src.star_system import StarSystem
from src.utilities import choose_from, confirm_input

class JumpScreen(PlayScreen):
    """Contains commands for the jump state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a JumpScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('inbound', 'Inbound to orbit', self.inbound_from_jump),
                Command('jump', 'Jump to new system', self.jump),
                Command('skim', 'Skim fuel from gas giant', self.skim),
                Command('damage control', 'Engineering damage control', self.damage_control),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Jump({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def inbound_from_jump(self) -> None:
        """Move from the jump point to orbit."""
        if self.model.in_deep_space():
            print(f"{BOLD_RED}You are in deep space. "
                  f"There is no inner system to travel to.{END_FORMAT}")
            return None

        if not self.model.can_maneuver():
            print(f"{BOLD_RED}Drive failure. Cannot travel to orbit.{END_FORMAT}")
            return None

        print(f"{BOLD_BLUE}Travelling in to orbit {self.model.system_name()}.{END_FORMAT}")

        leg_fc = self.model.check_fuel_level()
        if not leg_fc:
            print("Insufficient fuel to travel in from the jump point.")
            return None

        self.model.burn_fuel(leg_fc)
        self.model.add_day()
        self.model.set_location("orbit")
        self.parent.change_state("Orbit")
        return None

    # ACTIONS ==============================================================
    def jump(self) -> None:
        """Perform a hyperspace jump to another StarSystem."""
        print(f"{BOLD_BLUE}Preparing for jump.{END_FORMAT}")

        status = self.model.maintenance_status()
        self.model.check_failure_pre_jump(status)

        if not self.model.can_jump():
            print(f"{BOLD_RED}Drive failure. Cannot perform jump.{END_FORMAT}")
            return

        if not self.model.sufficient_jump_fuel():
            print(self.model.insufficient_jump_fuel_message())
            return

        if not self.model.sufficient_life_support():
            print(self.model.insufficient_life_support_message())
            return

        jump_range = self.model.jump_range
        print(f"Systems within jump-{jump_range}:")
        destinations = self.model.destinations
        destination_number = choose_from(destinations, "Enter destination number: ")

        coordinate = destinations[destination_number].coordinate
        destination = cast(StarSystem,
                           self.model.get_system_at_coordinate(coordinate))

        self.model.warn_if_not_contracted(destination)

        confirmation = confirm_input(f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling jump.")
            return

        self.model.check_unrefined_jump()

        print(f"{BOLD_RED}Executing jump!{END_FORMAT}")

        print(self.model.misjump_check(coordinate))

        self.model.perform_jump(self.parent, destination)

    def skim(self) -> None:
        """Refuel the Ship by skimming from a gas giant planet."""
        print(f"{BOLD_BLUE}Skimming fuel from a gas giant planet.{END_FORMAT}")
        print(self.model.skim())

    def damage_control(self) -> None:
        """Repair damage to the Ship (Engineer)."""
        print(f"{BOLD_BLUE}Ship's engineer repairing damage.{END_FORMAT}")
        print(self.model.damage_control())
