"""Contains the JumpScreen class.

JumpScreen - contains commands for the jump state.
"""
from typing import Any, cast
from src.command import Command
from src.cargo_depot import CargoDepot
from src.coordinate import Coordinate, get_misjump_target
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.model import Model
from src.play import PlayScreen
from src.ship import FuelQuality
from src.star_system import DeepSpace, StarSystem
from src.utilities import die_roll, choose_from, confirm_input

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
        if isinstance(self.model.location, DeepSpace):
            print(f"{BOLD_RED}You are in deep space. "
                  f"There is no inner system to travel to.{END_FORMAT}")
            return None

        print(f"{BOLD_BLUE}Travelling in to orbit {self.model.system_name()}.{END_FORMAT}")

        if not self.model.can_travel():
            print(f"{BOLD_RED}Drive failure. Cannot travel to orbit.{END_FORMAT}")
            return None

        leg_fc = self._check_fuel_level("in from")
        if not leg_fc:
            return None

        self.model.ship.current_fuel -= leg_fc
        self.model.add_day()
        self.model.set_location("orbit")
        self.parent.change_state("Orbit")
        return None

    # ACTIONS ==============================================================
    def jump(self) -> None:
        """Perform a hyperspace jump to another StarSystem."""
        print(f"{BOLD_BLUE}Preparing for jump.{END_FORMAT}")

        status = self.model.financials.maintenance_status(
                                     self.model.date.current_date)
        self.model.ship.check_failure_pre_jump(status)

        if not self.model.can_jump():
            print(f"{BOLD_RED}Drive failure. Cannot perform jump.{END_FORMAT}")
            return

        if not self.model.ship.sufficient_jump_fuel():
            print(self.model.ship.insufficient_jump_fuel_message())
            return

        if not self.model.ship.sufficient_life_support():
            print(self.model.ship.insufficient_life_support_message())
            return

        jump_range = self.model.ship.model.jump_range
        print(f"Systems within jump-{jump_range}:")
        destinations = self.model.location.destinations
        destination_number = choose_from(destinations, "Enter destination number: ")

        coordinate = destinations[destination_number].coordinate
        destination = cast(StarSystem,
                           self.model.star_map.get_system_at_coordinate(coordinate))

        self.model.ship.warn_if_not_contracted(destination)

        confirmation = confirm_input(f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling jump.")
            return

        if self.model.ship.fuel_quality == FuelQuality.UNREFINED:
            self.model.ship.unrefined_jump_counter += 1

        print(f"{BOLD_RED}Executing jump!{END_FORMAT}")

        self._misjump_check(coordinate)
        self.model.set_location("jump")

        self.model.ship.check_failure_post_jump()

        coord = self.model.location.coordinate
        self.model.location.destinations = \
              self.model.star_map.get_systems_within_range(coord, jump_range)

        self.model.depot = CargoDepot(self.model.location,
                                       self.model.date.current_date)
        self.model.depot.add_observer(self.parent)
        self.model.depot.controls = self.parent
        self.model.financials.location = destination

        self.model.ship.life_support_level = 0
        self.model.ship.current_fuel -= self.model.ship.model.jump_fuel_cost
        self.model.date.plus_week()

    def _misjump_check(self, destination: Coordinate) -> None:
        """Test for misjump and report results."""
        if self.model.ship.fuel_quality == FuelQuality.UNREFINED:
            modifier = 3
        else:
            modifier = -1
        if self.model.financials.maintenance_status(
                                self.model.date.current_date) == "red":
            modifier += 2

        misjump_check = die_roll(2) + modifier
        if misjump_check > 11:
            print(f"{BOLD_RED}MISJUMP!{END_FORMAT}")
            misjump_target, distance = get_misjump_target(self.model.location.coordinate)
            print(f"{misjump_target} at distance {distance}")

            # misjump is the only scenario where EmptySpace is a possible
            # location, so we need to leave this type as Hex
            loc = self.model.star_map.get_system_at_coordinate(misjump_target) # type: ignore
            self.model.location = loc                                          # type: ignore
            self.model.star_map.systems[misjump_target] = self.model.location
        else:
            self.model.location = cast(StarSystem,
                    self.model.star_map.get_system_at_coordinate(destination))

    # Book 2 p. 35
    # Unrefined fuel may be obtained by skimming the atmosphere of a
    # gas giant if unavailable elsewhere. Most star systems have at
    # least one...
    #
    # Traveller '77 does not restrict this to streamlined ships, and
    # also does not include ocean refuelling, but I think I will be
    # including both options. (In all likelihood this will lean heavily
    # toward second edition...)
    def skim(self) -> None:
        """Refuel the Ship by skimming from a gas giant planet."""
        print(f"{BOLD_BLUE}Skimming fuel from a gas giant planet.{END_FORMAT}")
        if not self.model.location.gas_giant:
            if isinstance(self.model.location, DeepSpace):
                print("You are stranded in deep space. No fuel skimming possible.")
            else:
                print("There is no gas giant in this system. No fuel skimming possible.")
            return

        if not self.model.ship.model.streamlined:
            print("Your ship is not streamlined and cannot skim fuel.")
            return

        if not self.model.can_travel():
            print(f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")
            return

        if self.model.ship.current_fuel == self.model.ship.model.fuel_tank:
            print("Fuel tank is already full.")
            return

        self.model.ship.current_fuel = self.model.ship.model.fuel_tank
        self.model.ship.fuel_quality = FuelQuality.UNREFINED
        self.model.add_day()

    def damage_control(self) -> None:
        """Repair damage to the Ship (Engineer)."""
        print(f"{BOLD_BLUE}Ship's engineer repairing damage.{END_FORMAT}")
        print(self.model.damage_control())
