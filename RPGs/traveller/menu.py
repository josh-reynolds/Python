"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from abc import ABC, abstractmethod
from random import randint, choice
from time import sleep
from typing import Any, List, TypeVar, cast, Tuple
from cargo import Baggage, PassageClass, Passenger, CargoDepot, Cargo, Freight
from command import Command
from coordinate import Coordinate
from financials import Credits
from ship import FuelQuality, RepairStatus
from star_system import DeepSpace, StarSystem, Hex
from utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT, confirm_input
from utilities import YELLOW_ON_RED, BOLD_BLUE, pr_list, pr_highlight_list, die_roll
from utilities import int_input

# pylint: disable=C0302
# C0302: Too many lines in module (1078/1000)

# keeping command characters straight...
# ALWAYS:   ? a ~ c d e ~ ~ h ~ ~ k ~ ~ ~ ~ ~ q ~ ~ ~ ~ v w ~ ~ z
# STARPORT:             f           l m n   p   r   t u
# ORBIT:                  g         l
# JUMP:                       i j                 s
# TRADE:        b       f g         l             s   u
# PASSENGERS:   b                   l

# TO_DO: might be helpful to have unit test to trap whether any keys
#        have been duplicated and thus overwritten

ScreenT = TypeVar("ScreenT", bound="Screen")

class Screen(ABC):
    """Base class for game screens."""

    def __init__(self, parent: Any) -> None:
        """Create a Screen object."""
        self.parent = parent
        self.commands: List[Command] = []

    def get_command(self, prompt: str) -> None | ScreenT:
        """Get command input from player and execute it."""
        while True:
            command = input(prompt)
            for cmd in self.commands:
                if command.lower() == cmd.key:
                    print()
                    result = cmd.action()
                    sleep(1)
                    return result

    @abstractmethod
    def update(self: ScreenT) -> ScreenT:
        """Draw the screen and gather input."""

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def quit(self) -> None:
        """Quit the game."""
        print(f"{BOLD_BLUE}Goodbye.{END_FORMAT}")
        self.parent.running = False

    # ACTIONS ==============================================================


class Menu(Screen):
    """Draws the menu screen and gathers input from the player."""

    def __init__(self, parent: Any) -> None:
        """Create a Menu object."""
        super().__init__(parent)
        self.commands: List[Command] = [
                Command('n', 'New Game', self.new_game),
                Command('l', 'Load Game', self.load_game),
                Command('q', 'Quit', self.quit),
                ]

    def update(self: ScreenT) -> ScreenT:
        """Draw the screen and present menu choices."""
        # ASCII art from https://patorjk.com/software
        # 'Grafitti' font
        title_lines = get_lines("title.txt")
        string = "Welcome to the Traveller Trading Game!"

        print(f"{HOME}{CLEAR}")
        for line in title_lines:
            line = line[:-1]    # strip newline char
            print(f"{BOLD_RED}{line}{END_FORMAT}")
        print(f"{BOLD}\n{string}{END_FORMAT}")

        for command in self.commands:
            print(f"{command.key} - {command.description}")

        new_state = self.get_command("\nEnter a command:  ")

        if new_state:
            return new_state
        return self

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================
    def new_game(self: ScreenT) -> ScreenT:
        """Start a new game."""
        self.parent.ship.name = input("What is the name of your ship? ")
        _ = input("Press ENTER key to continue.")
        return cast(ScreenT, Orbit(self.parent))

    def load_game(self) -> None:
        """Load a previous game."""
        _ = input("Press ENTER key to continue.")


class Play(Screen):
    """Draws the play screen and gathers input from the player.

    Base class for all Play screens.
    """

    def __init__(self, parent: Any) -> None:
        """Create a Play Screen object."""
        super().__init__(parent)
        self.commands: List[Command] = [
                Command('?', 'List commands', self.list_commands),
                Command('a', 'View star map', self.view_map),
                Command('c', 'Cargo hold contents', self.cargo_hold),
                Command('d', 'Passenger manifest', self.passenger_manifest),
                Command('e', 'Crew roster', self.crew_roster),
                Command('h', 'View ship details', self.view_ship),
                Command('k', 'Engineering damage control', self.damage_control),
                Command('q', 'Quit', self.quit),
                Command('v', 'View world characteristics', self.view_world),
                Command('w', 'Wait a week', self.wait_week),
                Command('z', 'Save Game', self.save_game),
                ]

    def update(self: ScreenT) -> ScreenT:
        """Draw the screen and present play choices."""
        if self.parent.ship.fuel_quality == FuelQuality.UNREFINED:
            fuel_quality = "(U)"
        else:
            fuel_quality = ""

        repair_state = ""
        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            repair_state = "\tDRIVE FAILURE - UNABLE TO JUMP OR MANEUVER"
        elif self.parent.ship.repair_status == RepairStatus.PATCHED:
            repair_state = "\tSEEK REPAIRS - UNABLE TO JUMP"

        fuel_amount = f"{self.parent.ship.current_fuel}/{self.parent.ship.fuel_tank}"

        print(f"{HOME}{CLEAR}")
        print(f"{YELLOW_ON_RED}\n{self.parent.date} : You are " +
              f"{self.parent.location.description()}.{repair_state}{END_FORMAT}")
        print(f"Credits: {self.parent.financials.balance}"
              f"\tFree hold space: {self.parent.ship.free_space()} tons"
              f"\tFuel: {fuel_amount} tons {fuel_quality}"
              f"\tLife support: {self.parent.ship.life_support_level}%")

        new_state = self.get_command("Enter a command (? to list):  ")

        if new_state:
            return new_state
        return self

    # VIEW COMMANDS ========================================================
    def list_commands(self) -> None:
        """List available commands in the current context."""
        print(f"{BOLD_BLUE}Available commands:{END_FORMAT}")
        for command in self.commands:
            print(f"{command.key} - {command.description}")
        _ = input("\nPress ENTER key to continue.")

    def view_world(self) -> None:
        """View the characteristics of the local world."""
        print(f"{BOLD_BLUE}Local world characteristics:{END_FORMAT}")
        coord = self.parent.location.coordinate.trav_coord
        sub_string = self.parent.star_map.pretty_coordinates(coord)
        print(f"{sub_string} : {self.parent.location}")
        _ = input("\nPress ENTER key to continue.")

    def cargo_hold(self) -> None:
        """Show the contents of the Ship's cargo hold."""
        print(f"{BOLD_BLUE}Contents of cargo hold:{END_FORMAT}")
        contents = self.parent.ship.cargo_hold()
        if len(contents) == 0:
            print("Empty.")
        else:
            pr_list(contents)
        _ = input("\nPress ENTER key to continue.")

    def passenger_manifest(self) -> None:
        """Show the Passengers booked for transport."""
        print(f"{BOLD_BLUE}Passenger manifest:{END_FORMAT}")
        if self.parent.ship.destination is None:
            destination = "None"
        else:
            destination = self.parent.ship.destination.name
        print(f"High passengers: {self.parent.ship.high_passenger_count}\n"
              f"Middle passengers: {self.parent.ship.middle_passenger_count}\n"
              f"Low passengers: {self.parent.ship.low_passenger_count}\n"
              f"DESTINATION: {destination}\n\n"
              f"Empty berths: {self.parent.ship.empty_passenger_berths}\n"
              f"Empty low berths: {self.parent.ship.empty_low_berths}")
        _ = input("\nPress ENTER key to continue.")

    def crew_roster(self) -> None:
        """Show the Ship's crew."""
        print(f"{BOLD_BLUE}Crew roster:{END_FORMAT}")
        pr_list(self.parent.ship.crew)
        _ = input("\nPress ENTER key to continue.")

    def view_ship(self) -> None:
        """View the details of the Ship."""
        print(f"{BOLD_BLUE}Ship details:{END_FORMAT}")
        print(self.parent.ship)
        _ = input("\nPress ENTER key to continue.")

    # TO_DO: some duplication with view_world() - refactor
    def view_map(self) -> None:
        """View all known StarSystems."""
        print(f"{BOLD_BLUE}All known star systems:{END_FORMAT}")
        systems = self.parent.star_map.get_all_systems()
        system_strings = []
        for sys in systems:
            coord = sys.coordinate.trav_coord
            sub_string = self.parent.star_map.pretty_coordinates(coord)
            combined = f"{sub_string} : {sys}"
            system_strings.append(combined)
        # BUG: change to list of strings breaks highlighting functionality
        pr_highlight_list(system_strings, self.parent.location, "\t<- CURRENT LOCATION")
        _ = input("\nPress ENTER key to continue.")

    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================

    # TO_DO: should this method move to jump point? Only needed/useful
    #        when the ship is BROKEN, which only happens at the jp.
    def damage_control(self) -> None:
        """Repair damage to the Ship (Engineer)."""
        print(f"{BOLD_BLUE}Ship's engineer repairing damage.{END_FORMAT}")
        if self.parent.ship.repair_status == RepairStatus.REPAIRED:
            print("Your ship is not damaged.")
            return
        if self.parent.ship.repair_status == RepairStatus.PATCHED:
            print("Further repairs require starport facilities.")
            return
        self.parent.date.day += 1
        if die_roll(2) + self.parent.ship.engineering_skill() > 9:
            self.parent.ship.repair_status = RepairStatus.PATCHED
            print("Ship partially repaired. Visit a starport for further work.")
        else:
            print("No progress today. Drives are still out of commission.")

    def save_game(self) -> None:
        """Save current game state."""
        print(f"{BOLD_BLUE}Saving game.{END_FORMAT}")
        systems = self.parent.star_map.get_all_systems()
        with open('save_game.txt', 'w', encoding='utf-8') as out_file:
            for entry in systems:
                out_file.write(str(entry) + "\n")

    def wait_week(self) -> None:
        """Advance the Calendar by seven days."""
        print(f"{BOLD_BLUE}Waiting.{END_FORMAT}")
        self.parent.date.plus_week()


class Orbit(Play):
    """Contains commands for the Orbit state."""

    def __init__(self, parent: Any) -> None:
        """Create an Orbit object."""
        super().__init__(parent)
        self.commands += [
                Command('l', 'Land at starport', self.land),
                Command('g', 'Go to jump point', self.outbound_to_jump),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def land(self: ScreenT) -> None | ScreenT:
        """Move from orbit to the starport."""
        print(f"{BOLD_BLUE}Landing on {self.parent.location.name}.{END_FORMAT}")
        if not self.parent.ship.streamlined:
            print("Your ship is not streamlined and cannot land.")
            return None

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot land.{END_FORMAT}")
            return None

        if self.parent.ship.destination == self.parent.location:
            if self.parent.ship.total_passenger_count > 0:
                print(f"Passengers disembarking on {self.parent.location.name}.")

                funds = Credits(sum(p.ticket_price.amount for p in self.parent.ship.passengers))
                low_lottery_amount = Credits(10) * self.parent.ship.low_passenger_count
                funds -= low_lottery_amount
                print(f"Receiving {funds} in passenger fares.")
                self.parent.financials.credit(funds)

                # annotations want ScreenT to have this method
                self._low_lottery(low_lottery_amount)      #type: ignore[attr-defined]

                self.parent.ship.passengers = []
                self.parent.ship.hold = [item for item in self.parent.ship.hold
                                  if not isinstance(item, Baggage)]

        self.parent.financials.berthing_fee(self.parent.location.on_surface())
        self.parent.location.detail = "starport"
        return cast(ScreenT, Starport(self.parent))

    def _low_lottery(self, low_lottery_amount) -> None:
        """Run the low passage lottery and apply results."""
        if self.parent.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.parent.ship.passengers if
                                         p.passage == PassageClass.LOW]
            for passenger in low_passengers:
                if die_roll(2) + passenger.endurance + self.parent.ship.medic_skill() < 5:
                    passenger.survived = False

            survivors = [p for p in low_passengers if p.survived]
            print(f"{len(survivors)} of {len(low_passengers)} low passengers "
                  "survived revival.")

            winner = False
            for passenger in low_passengers:
                if passenger.guess == len(survivors) and passenger.survived:
                    winner = True

            if not winner:
                print(f"No surviving low lottery winner. "
                      f"The captain is awarded {low_lottery_amount}.")
                self.parent.financials.credit(low_lottery_amount)

    def outbound_to_jump(self: ScreenT) -> None | ScreenT:
        """Move from orbit to the jump point."""
        print(f"{BOLD_BLUE}Travelling out to {self.parent.location.name} jump point.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot travel to the jump point.{END_FORMAT}")
            return None

        leg_fc = self.parent.ship.trip_fuel_cost // 2
        if self.parent.ship.current_fuel < leg_fc:
            print(f"Insufficient fuel. Travel out to the jump point "
                  f"requires {leg_fc} tons, only "
                  f"{self.parent.ship.current_fuel} tons in tanks.")
            return None

        self.parent.ship.current_fuel -= leg_fc
        self.parent.date.day += 1
        self.parent.location.detail = "jump"
        return cast(ScreenT, Jump(self.parent))

    # ACTIONS ==============================================================

class Starport(Play):
    """Contains commands for the Starport state."""

    def __init__(self, parent: Any) -> None:
        """Create a Starport object."""
        super().__init__(parent)
        self.commands += [
                Command('f', 'Recharge life support', self.recharge),
                Command('r', 'Refuel', self.refuel),
                Command('l', 'Lift off to orbit', self.liftoff),
                Command('t', 'Trade depot', self.to_depot),
                Command('p', 'Passenger terminal', self.to_terminal),
                Command('m', 'Annual maintenance', self.maintenance),
                Command('u', 'Flush fuel tanks', self.flush),
                Command('n', 'Repair ship', self.repair_ship),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def liftoff(self: ScreenT) -> None | ScreenT:
        """Move from the starport to orbit."""
        print(f"{BOLD_BLUE}Lifting off to orbit {self.parent.location.name}.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot lift off.{END_FORMAT}")
            return None

        # corner case - these messages assume passengers are coming
        # from the current world, which should be true most
        # of the time, but not necessarily all the time
        if self.parent.ship.total_passenger_count > 0:
            print(f"Boarding {self.parent.ship.total_passenger_count} passengers "
                  f"for {self.parent.ship.destination.name}.")

        if self.parent.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.parent.ship.passengers if
                              p.passage == PassageClass.LOW]
            for passenger in low_passengers:
                passenger.guess_survivors(self.parent.ship.low_passenger_count)

        self.parent.location.detail = "orbit"
        return cast(ScreenT, Orbit(self.parent))

    def to_depot(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the trade depot."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} trade depot.{END_FORMAT}")
        self.parent.location.detail = "trade"
        return cast(ScreenT, Trade(self.parent))

    def to_terminal(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the passenger terminal."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} passenger terminal.{END_FORMAT}")
        self.parent.location.detail = "terminal"
        return cast(ScreenT, Passengers(self.parent))

    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        cost = self.parent.ship.recharge()
        self.parent.financials.debit(cost)

    def refuel(self) -> None:
        """Refuel the Ship."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        if self.parent.location.starport in ('E', 'X'):
            print(f"No fuel is available at starport {self.parent.location.starport}.")
            return

        cost = self.parent.ship.refuel(self.parent.location.starport)
        self.parent.financials.debit(cost)

    def maintenance(self) -> None:
        """Perform annual maintenance on the Ship."""
        print(f"{BOLD_BLUE}Performing annual ship maintenance.{END_FORMAT}")
        if self.parent.location.starport not in ('A', 'B'):
            print("Annual maintenance can only be performed at class A or B starports.")
            return

        cost = self.parent.ship.maintenance_cost()
        if self.parent.financials.balance < cost:
            print("You do not have enough funds to pay for maintenance.\n"
                  f"It will cost {cost}. Your balance is {self.parent.financials.balance}.")
            return

        # TO_DO: should we have a confirmation here?
        # TO_DO: should we warn or block if maintenance was performed recently?
        print(f"Performing maintenance. This will take two weeks. Charging {cost}.")
        self.parent.financials.last_maintenance = self.parent.date.current_date
        self.parent.financials.debit(cost)
        self.parent.date.day += 14    # should we wrap this in a method call?
        self.parent.ship.repair_status = RepairStatus.REPAIRED

    def flush(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        print(f"{BOLD_BLUE}Flushing out fuel tanks.{END_FORMAT}")
        if self.parent.ship.fuel_quality == FuelQuality.REFINED:
            print("Ship fuel tanks are clean. No need to flush.")
            return
        if self.parent.location.starport in ('E', 'X'):
            print(f"There are no facilities to flush tanks "
                  f"at starport {self.parent.location.starport}.")
            return

        print("Fuel tanks have been decontaminated.")
        self.parent.ship.fuel_quality = FuelQuality.REFINED
        self.parent.ship.unrefined_jump_counter = 0
        self.parent.date.plus_week()

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self) -> None:
        """Fully repair damage to the Ship (Starport)."""
        print(f"{BOLD_BLUE}Starport repairs.{END_FORMAT}")
        if self.parent.location.starport in ["D", "E", "X"]:
            print(f"No repair facilities available at starport {self.parent.location.starport}")
            return
        if self.parent.ship.repair_status == RepairStatus.REPAIRED:
            print("Your ship is not damaged.")
            return

        print("Your ship is fully repaired and decontaminated.")
        self.parent.ship.repair_status = RepairStatus.REPAIRED
        self.parent.ship.fuel_quality = FuelQuality.REFINED
        self.parent.ship.unrefined_jump_counter = 0
        self.parent.date.plus_week()


class Jump(Play):
    """Contains commands for the Jump state."""

    def __init__(self, parent: Any) -> None:
        """Create a Jump object."""
        super().__init__(parent)
        self.commands += [
                Command('i', 'Inbound to orbit', self.inbound_from_jump),
                Command('j', 'Jump to new system', self.jump),
                Command('s', 'Skim fuel from gas giant', self.skim),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def inbound_from_jump(self: ScreenT) -> None | ScreenT:
        """Move from the jump point to orbit."""
        if isinstance(self.parent.location, DeepSpace):
            print(f"{BOLD_RED}You are in deep space. "
                  f"There is no inner system to travel to.{END_FORMAT}")
            return None

        print(f"{BOLD_BLUE}Travelling in to orbit {self.parent.location.name}.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot travel to orbit.{END_FORMAT}")
            return None

        leg_fc = self.parent.ship.trip_fuel_cost // 2
        if self.parent.ship.current_fuel < leg_fc:
            print(f"Insufficient fuel. Travel in from the jump point "
                  f"requires {leg_fc} tons, only "
                  f"{self.parent.ship.current_fuel} tons in tanks.")
            return None

        self.parent.ship.current_fuel -= leg_fc
        self.parent.date.day += 1
        self.parent.location.detail = "orbit"
        return cast(ScreenT, Orbit(self.parent))

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

        jump_range = self.parent.ship.jump_range
        print(f"Systems within jump-{jump_range}:")
        pr_list(self.parent.location.destinations)
        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(self.parent.location.destinations):
            print("That is not a valid destination number.")
            return

        coordinate = self.parent.location.destinations[destination_number].coordinate
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
        self.parent.ship.current_fuel -= self.parent.ship.jump_fuel_cost
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
            hexes = [(0,distance,-distance),
                     (0,-distance,distance),
                     (distance,0,-distance),
                     (-distance,0,distance),
                     (distance,-distance,0),
                     (-distance,distance,0)]
            misjump_target = choice(hexes)
            misjump_target = (misjump_target[0] + self.parent.location.coordinate[0],
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

        if not self.parent.ship.streamlined:
            print("Your ship is not streamlined and cannot skim fuel.")
            return

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")
            return

        if self.parent.ship.current_fuel == self.parent.ship.fuel_tank:
            print("Fuel tank is already full.")
            return

        self.parent.ship.current_fuel = self.parent.ship.fuel_tank
        self.parent.ship.fuel_quality = FuelQuality.UNREFINED
        self.parent.date.day += 1


class Trade(Play):
    """Contains commands for the Trade state."""

    def __init__(self, parent: Any) -> None:
        """Create a Trade object."""
        super().__init__(parent)
        self.commands += [
                Command('l', 'Leave trade depot', self.leave_depot),
                Command('b', 'Buy cargo', self.buy_cargo),
                Command('s', 'Sell cargo', self.sell_cargo),
                Command('g', 'View trade goods', self.goods),
                Command('f', 'Load freight', self.load_freight),
                Command('u', 'Unload freight', self.unload_freight),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    def goods(self) -> None:
        """Show goods available for purchase."""
        print(f"{BOLD_BLUE}Available cargo loads:{END_FORMAT}")
        pr_list(self.parent.depot.cargo)
        _ = input("\nPress ENTER key to continue.")

    # STATE TRANSITIONS ====================================================
    def leave_depot(self: ScreenT) -> None | ScreenT:
        """Move from the trade depot to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.parent.location.name} trade depot.{END_FORMAT}")
        self.parent.location.detail = "starport"
        return cast(ScreenT, Starport(self.parent))

    # ACTIONS ==============================================================
    def buy_cargo(self) -> None:
        """Purchase cargo for speculative trade."""
        print(f"{BOLD_BLUE}Purchasing cargo.{END_FORMAT}")
        pr_list(self.parent.depot.cargo)
        cargo = self.parent.depot.get_cargo_lot(self.parent.depot.cargo, "buy")
        if cargo is None:
            return

        quantity = self.parent.depot.get_cargo_quantity("buy", cargo)
        if quantity is None:
            return

        if self.parent.depot.insufficient_hold_space(cargo,
                                                     quantity,
                                                     self.parent.ship.free_space()):
            return

        cost = self.parent.depot.determine_price("purchase", cargo, quantity,
                                          self.parent.ship.trade_skill())

        if self.parent.depot.insufficient_funds(cost, self.parent.financials.balance):
            return

        if not self.parent.depot.confirm_transaction("purchase", cargo, quantity, cost):
            return

        self.parent.depot.remove_cargo(self.parent.depot.cargo, cargo, quantity)

        purchased = Cargo(cargo.name, str(quantity), cargo.price, cargo.unit_size,
                          cargo.purchase_dms, cargo.sale_dms, self.parent.location)
        self.parent.ship.load_cargo(purchased)

        self.parent.financials.debit(cost)
        self.parent.date.day += 1

    def sell_cargo(self) -> None:
        """Sell cargo in speculative trade."""
        print(f"{BOLD_BLUE}Selling cargo.{END_FORMAT}")
        cargoes = [c for c in self.parent.ship.hold if isinstance(c, Cargo)]

        if len(cargoes) == 0:
            print("You have no cargo on board.")
            return

        pr_list(cargoes)
        cargo = self.parent.depot.get_cargo_lot(cargoes, "sell")
        if cargo is None:
            return

        if self.parent.depot.invalid_cargo_origin(cargo):
            return

        broker_skill = self.parent.depot.get_broker()

        quantity = self.parent.depot.get_cargo_quantity("sell", cargo)
        if quantity is None:
            return

        sale_price = self.parent.depot.determine_price("sale", cargo, quantity,
                                                broker_skill + self.parent.ship.trade_skill())

        self.parent.financials.debit(self.parent.depot.broker_fee(broker_skill, sale_price))

        if not self.parent.depot.confirm_transaction("sale", cargo, quantity, sale_price):
            return

        self.parent.depot.remove_cargo(self.parent.ship.hold, cargo, quantity)

        self.parent.financials.credit(sale_price)
        self.parent.date.day += 1

    def load_freight(self) -> None:
        """Select and load Freight onto the Ship."""
        print(f"{BOLD_BLUE}Loading freight.{END_FORMAT}")

        jump_range = self.parent.ship.jump_range
        potential_destinations = self.parent.location.destinations.copy()
        destinations = self._get_freight_destinations(potential_destinations, jump_range)
        if not destinations:
            return

        coordinate, available = self.parent.depot.get_available_freight(destinations)
        if available is None:
            return

        destination = cast(StarSystem,
                           self.parent.star_map.get_system_at_coordinate(
                               cast(Coordinate, coordinate)))
        print(f"Freight shipments for {destination.name}")
        print(available)

        total_tonnage, selection = self._select_freight_lots(available, destination)

        if total_tonnage == 0:
            print("No freight shipments selected.")
            return
        print(f"{total_tonnage} tons selected.")

        confirmation = confirm_input(f"Load {total_tonnage} tons of freight? (y/n)? ")
        if confirmation == 'n':
            print("Cancelling freight selection.")
            return

        for entry in selection:
            self.parent.depot.freight[destination].remove(entry)
            self.parent.ship.load_cargo(Freight(entry,
                                         self.parent.location,
                                         destination))
        self.parent.date.day += 1

    def _get_freight_destinations(self, potential_destinations: List[StarSystem],
                                  jump_range: int) -> List[StarSystem]:
        """Return a list of all reachable destinations with Freight lots."""
        result: List[StarSystem] = []
        if self.parent.ship.destination is not None:
            if self.parent.ship.destination == self.parent.location:
                print(f"{BOLD_RED}There is still freight to be unloaded "
                      f"on {self.parent.location.name}.{END_FORMAT}")
                return result
            if self.parent.ship.destination in potential_destinations:
                print("You are under contract. Only showing freight " +
                      f"for {self.parent.ship.destination.name}:\n")
                result = [self.parent.ship.destination]
            else:
                print(f"You are under contract to {self.parent.ship.destination.name} " +
                      "but it is not within jump range of here.")

        else:
            print(f"Available freight shipments within jump-{jump_range}:\n")
            result = potential_destinations

        return result

    def _select_freight_lots(self, available: List[int],
                             destination: Hex) -> Tuple[int, List[int]]:
        """Select Freight lots from a list of available shipments."""
        selection: List[int] = []
        total_tonnage = 0
        hold_tonnage = self.parent.ship.free_space()
        while True:
            if len(available) == 0:
                print(f"No more freight available for {destination.name}.")
                break

            # can't use int input here since we allow for 'q' as well...
            response: int | str = input("Choose a shipment by tonnage ('q' to exit): ")
            if response == 'q':
                break

            try:
                response = int(response)
            except ValueError:
                print("Please input a number.")
                continue

            if response in available:
                if response <= hold_tonnage:
                    # even though we cast to int above in try/catch,
                    # mypy is unaware, need to cast again to silence it.
                    # sort this out...
                    available.remove(cast(int, response))
                    selection.append(cast(int, response))
                    total_tonnage += response
                    hold_tonnage -= response
                    print(available)
                    print(f"Cargo space left: {hold_tonnage}")
                else:
                    print(f"{BOLD_RED}That shipment will not fit in your cargo hold.{END_FORMAT}")
                    print(f"{BOLD_RED}Hold free space: {hold_tonnage}{END_FORMAT}")
            else:
                print(f"{BOLD_RED}There are no shipments of size {response}.{END_FORMAT}")

        print("Done selecting shipments.")
        return (total_tonnage, selection)

    def unload_freight(self) -> None:
        """Unload Freight from the Ship and receive payment."""
        print(f"{BOLD_BLUE}Unloading freight.{END_FORMAT}")

        # truth table: passengers, freight, destination flag,...

        # It should not be possible for there to be freight in the hold,
        # and a destination flag set to None. Should we assert just
        # in case, so we could track down any such bug:
        if self.parent.ship.destination is None:
            print("You have no contracted destination.")
            return

        freight = [f for f in self.parent.ship.hold if isinstance(f, Freight)]
        if len(freight) == 0:
            print("You have no freight on board.")
            return

        if self.parent.ship.destination == self.parent.location:
            freight_tonnage = sum(f.tonnage for f in freight)
            self.parent.ship.hold = [c for c in self.parent.ship.hold if isinstance(c, Cargo)]

            payment = Credits(1000 * freight_tonnage)
            self.parent.financials.credit(Credits(1000 * freight_tonnage))
            print(f"Receiving payment of {payment} for {freight_tonnage} tons shipped.")

            self.parent.date.day += 1

        else:
            print(f"{BOLD_RED}You are not at the contracted "
                  f"destination for this freight.{END_FORMAT}")
            print(f"{BOLD_RED}It should be unloaded at "
                  f"{self.parent.ship.destination.name}.{END_FORMAT}")


class Passengers(Play):
    """Contains commands for the Passengers state."""

    def __init__(self, parent: Any) -> None:
        """Create a Passengers object."""
        super().__init__(parent)
        self.commands += [
                Command('l', 'Leave terminal', self.leave_terminal),
                Command('b', 'Book passengers', self.book_passengers),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def leave_terminal(self: ScreenT) -> None | ScreenT:
        """Move from the passenger terminal to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.parent.location.name} passenger terminal.{END_FORMAT}")
        self.parent.location.detail = "starport"
        return cast(ScreenT, Starport(self.parent))

    # ACTIONS ==============================================================
    def book_passengers(self) -> None:
        """Book passengers for travel to a destination."""
        print(f"{BOLD_BLUE}Booking passengers.{END_FORMAT}")

        jump_range = self.parent.ship.jump_range
        potential_destinations = self.parent.location.destinations.copy()
        destinations = self._get_passenger_destinations(potential_destinations, jump_range)
        if not destinations:
            return

        # for now we will stuff this in cargo depot, though it may better
        # be served by a separate class. If it _does_ stay in the depot, we
        # may want to adjust the nomenclature to make this more clear.
        coordinate, available = self.parent.depot.get_available_passengers(destinations)
        if available is None:
            return

        destination = cast(StarSystem, self.parent.star_map.get_system_at_coordinate(coordinate))
        print(f"Passengers for {destination.name} (H,M,L): {available}")

        selection = self._select_passengers(available, destination)

        if selection == (0,0,0):
            print("No passengers selected.")
            return
        print(f"Selected (H, M, L): {selection}")

        confirmation = confirm_input(f"Book {selection} passengers? (y/n)? ")
        if confirmation == 'n':
            print("Cancelling passenger selection.")
            return

        # TO_DO: need to consider the case where we already have passengers
        #        Probably want to wrap passenger field access in a property...
        high = [Passenger(PassageClass.HIGH, destination)
                for _ in range(selection[PassageClass.HIGH.value])]
        baggage = [Baggage(self.parent.location, destination)
                   for _ in range(selection[PassageClass.HIGH.value])]
        middle = [Passenger(PassageClass.MIDDLE, destination)
                  for _ in range(selection[PassageClass.MIDDLE.value])]
        low = [Passenger(PassageClass.LOW, destination)
               for _ in range(selection[PassageClass.LOW.value])]

        self.parent.ship.passengers += high
        self.parent.ship.hold += baggage
        self.parent.ship.passengers += middle
        self.parent.ship.passengers += low
        self.parent.depot.passengers[destination] = tuple(a-b for a,b in
                                                   zip(self.parent.depot.passengers[destination],
                                                       selection))

    def _get_passenger_destinations(self, potential_destinations: List[StarSystem],
                                    jump_range: int) -> List[StarSystem]:
        """Return a list of all reachable destination with Passengers."""
        result: List[StarSystem] = []
        if self.parent.ship.destination is not None:
            if self.parent.ship.destination == self.parent.location:
                print(f"{BOLD_RED}There is still freight to be "
                      f"unloaded on {self.parent.location.name}.{END_FORMAT}")
                return result
            if self.parent.ship.destination in potential_destinations:
                print("You are under contract. Only showing passengers " +
                      f"for {self.parent.ship.destination.name}:\n")
                result = [self.parent.ship.destination]
            else:
                print(f"You are under contract to {self.parent.ship.destination.name} " +
                      "but it is not within jump range of here.")

        else:
            print(f"Available passenger destinations within jump-{jump_range}:\n")
            result = potential_destinations

        return result

    # pylint: disable=R0912, R0915
    # R0912: Too many branches (13/12)
    # R0915: Too many statements (51/50)
    def _select_passengers(self, available: Tuple[int, ...],
                           destination: Hex) -> Tuple[int, ...]:
        """Select Passengers from a list of available candidates."""
        selection: Tuple[int, ...] = (0,0,0)
        ship_capacity: Tuple[int, ...] = (self.parent.ship.empty_passenger_berths,
                                          self.parent.ship.empty_low_berths)

        ship_hold = self.parent.ship.free_space()
        while True:
            if available == (0,0,0):
                print(f"No more passengers available for {destination.name}.")
                break

            response = input("Choose a passenger by type (h, m, l) and number, or q to exit): ")
            if response == 'q':
                break

            print(f"Remaining (H, M, L): {available}")
            print(f"Selected (H, M, L): {selection}")
            print(f"Empty ship berths (H+M, L): {ship_capacity}\n")

            tokens = response.split()
            if len(tokens) != 2:
                print("Please enter in the format: passage number (example: h 5).")
                continue

            passage = tokens[0]
            if passage not in ['h', 'm', 'l']:
                print("Please enter 'h', 'm' or 'l' for passage class.")
                continue

            try:
                count = int(tokens[1])
            except ValueError:
                print("Please input a number.")
                continue

            suffix = ""
            if count > 1:
                suffix = "s"

            if passage == 'h':
                if self._no_passengers_available("high", available, count):
                    print("There are not enough high passengers available.")
                    continue
                if ship_capacity[0] - count < 0:
                    print("There are not enough staterooms available.")
                    continue
                if ship_hold - count < 0:
                    print("There is not enough cargo space available.")
                    continue
                print(f"Adding {count} high passenger{suffix}.")
                selection = tuple(a+b for a,b in zip(selection,(count,0,0)))
                available = tuple(a+b for a,b in zip(available,(-count,0,0)))
                ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-count,0)))
                ship_hold -= count

            if passage == 'm':
                if self._no_passengers_available("middle", available, count):
                    print("There are not enough middle passengers available.")
                    continue
                if ship_capacity[0] - count < 0:
                    print("There are not enough staterooms available.")
                    continue
                print(f"Adding {count} middle passenger{suffix}.")
                selection = tuple(a+b for a,b in zip(selection,(0,count,0)))
                available = tuple(a+b for a,b in zip(available,(0,-count,0)))
                ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-count,0)))

            if passage == 'l':
                if self._no_passengers_available("low", available, count):
                    print("There are not enough low passengers available.")
                    continue
                if ship_capacity[1] - count < 0:
                    print("There are not enough low berths available.")
                    continue
                print(f"Adding {count} low passenger{suffix}.")
                selection = tuple(a+b for a,b in zip(selection,(0,0,count)))
                available = tuple(a+b for a,b in zip(available,(0,0,-count)))
                ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(0,-count)))

        print("Done selecting passengers.")
        return selection

    def _no_passengers_available(self, passage: str, available: tuple, count: int) -> bool:
        if passage == "high":
            index = PassageClass.HIGH.value
        elif passage == "middle":
            index = PassageClass.MIDDLE.value
        else:
            index = PassageClass.LOW.value

        return available[index] - count < 0
