"""Contains the Jump screen class.

Jump - contains commands for the Jump state.
"""
from random import randint, choice
from typing import Any, cast
from src.command import Command
from src.cargo_depot import CargoDepot
from src.coordinate import Coordinate
from src.play import Play
from src.ship import RepairStatus, FuelQuality
from src.star_system import DeepSpace, StarSystem
from src.utilities import BOLD_BLUE, END_FORMAT, BOLD_RED, die_roll, choose_from, confirm_input

class Jump(Play):
    """Contains commands for the Jump state."""

    def __init__(self, parent: Any) -> None:
        """Create a Jump object."""
        super().__init__(parent)
        self.commands += [
                Command('inbound', 'Inbound to orbit', self.inbound_from_jump),
                Command('jump', 'Jump to new system', self.jump),
                Command('skim', 'Skim fuel from gas giant', self.skim),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __str__(self) -> str:
        """Return the string representation of the current screen."""
        return "Jump"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def inbound_from_jump(self) -> None:
        """Move from the jump point to orbit."""
        if isinstance(self.parent.location, DeepSpace):
            print(f"{BOLD_RED}You are in deep space. "
                  f"There is no inner system to travel to.{END_FORMAT}")
            return None

        print(f"{BOLD_BLUE}Travelling in to orbit {self.parent.location.name}.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot travel to orbit.{END_FORMAT}")
            return None

        leg_fc = self._check_fuel_level("in from")
        if not leg_fc:
            return None

        self.parent.ship.current_fuel -= leg_fc
        self.parent.date.day += 1
        self.parent.change_state("Orbit")
        return None

    # ACTIONS ==============================================================
    def jump(self) -> None:
        """Perform a hyperspace jump to another StarSystem."""
        print(f"{BOLD_BLUE}Preparing for jump.{END_FORMAT}")

        status = self.parent.financials.maintenance_status(self.parent.date.current_date)
        self.parent.ship.check_failure_pre_jump(status)
        if self.parent.ship.repair_status in (RepairStatus.BROKEN, RepairStatus.PATCHED):
            print(f"{BOLD_RED}Drive failure. Cannot perform jump.{END_FORMAT}")
            return

        if not self.parent.ship.sufficient_jump_fuel():
            print(self.parent.ship.insufficient_jump_fuel_message())
            return

        if not self.parent.ship.sufficient_life_support():
            print(self.parent.ship.insufficient_life_support_message())
            return

        jump_range = self.parent.ship.model.jump_range
        print(f"Systems within jump-{jump_range}:")
        destinations = self.parent.location.destinations
        destination_number = choose_from(destinations, "Enter destination number: ")

        coordinate = destinations[destination_number].coordinate
        destination = cast(StarSystem, self.parent.star_map.get_system_at_coordinate(coordinate))

        self.parent.ship.warn_if_not_contracted(destination)

        confirmation = confirm_input(f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling jump.")
            return

        if self.parent.ship.fuel_quality == FuelQuality.UNREFINED:
            self.parent.ship.unrefined_jump_counter += 1

        print(f"{BOLD_RED}Executing jump!{END_FORMAT}")

        self._misjump_check(coordinate)
        self.parent.location.detail = "jump"

        self.parent.ship.check_failure_post_jump()

        coord = self.parent.location.coordinate
        self.parent.location.destinations = self.parent.star_map.get_systems_within_range(coord,
                                                   jump_range)

        self.parent.depot = CargoDepot(self.parent.location, self.parent.date.current_date)
        self.parent.depot.add_observer(self.parent)
        self.parent.depot.controls = self.parent
        self.parent.financials.location = destination

        self.parent.ship.life_support_level = 0
        self.parent.ship.current_fuel -= self.parent.ship.model.jump_fuel_cost
        self.parent.date.plus_week()

    def _misjump_check(self, destination: Coordinate) -> None:
        """Test for misjump and report results."""
        if self.parent.ship.fuel_quality == FuelQuality.UNREFINED:
            modifier = 3
        else:
            modifier = -1
        if self.parent.financials.maintenance_status(self.parent.date.current_date) == "red":
            modifier += 2

        misjump_check = die_roll(2) + modifier
        if misjump_check > 11:
            print(f"{BOLD_RED}MISJUMP!{END_FORMAT}")
            # TO_DO: all this should move to live with the other
            #        three-axis calculations
            distance = randint(1,36)
            hexes = [Coordinate(0,distance,-distance),
                     Coordinate(0,-distance,distance),
                     Coordinate(distance,0,-distance),
                     Coordinate(-distance,0,distance),
                     Coordinate(distance,-distance,0),
                     Coordinate(-distance,distance,0)]
            misjump_target = choice(hexes)
            misjump_target = Coordinate(misjump_target[0] + self.parent.location.coordinate[0],
                                        misjump_target[1] + self.parent.location.coordinate[1],
                                        misjump_target[2] + self.parent.location.coordinate[2])
            print(f"{misjump_target} at distance {distance}")

            # misjump is the only scenario where EmptySpace is a possible
            # location, so we need to leave this type as Hex
            loc = self.parent.star_map.get_system_at_coordinate(misjump_target) # type: ignore
            self.parent.location = loc
            self.parent.star_map.systems[misjump_target] = self.parent.location
        else:
            self.parent.location = cast(StarSystem,
                                        self.parent.star_map.get_system_at_coordinate(destination))

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
        if not self.parent.location.gas_giant:
            # TO_DO: may want to tweak this message in deep space.
            print("There is no gas giant in this system. No fuel skimming possible.")
            return

        if not self.parent.ship.model.streamlined:
            print("Your ship is not streamlined and cannot skim fuel.")
            return

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")
            return

        if self.parent.ship.current_fuel == self.parent.ship.model.fuel_tank:
            print("Fuel tank is already full.")
            return

        self.parent.ship.current_fuel = self.parent.ship.model.fuel_tank
        self.parent.ship.fuel_quality = FuelQuality.UNREFINED
        self.parent.date.day += 1
