"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from abc import ABC, abstractmethod
from time import sleep
from typing import Any, List, TypeVar, cast
from cargo import Baggage, PassageClass
from command import Command
from financials import Credits
from ship import FuelQuality, RepairStatus
from utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT
from utilities import YELLOW_ON_RED, BOLD_BLUE, pr_list, pr_highlight_list, die_roll

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
                Command('q', 'Quit', self.quit)
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
                Command('s', 'Save Game', self.save_game),
                Command('v', 'View world characteristics', self.view_world),
                Command('w', 'Wait a week', self.wait_week),
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
        print(self.parent.location)
        _ = input("\nPress ENTER key to continue.")

    # TO_DO: Should only be usable from the trade depot location
    def goods(self) -> None:
        """Show goods available for purchase."""
        print(f"{BOLD_BLUE}Available cargo loads:{END_FORMAT}")
        pr_list(self.parent.depot.cargo)
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

    def view_map(self) -> None:
        """View all known StarSystems."""
        print(f"{BOLD_BLUE}All known star systems:{END_FORMAT}")
        systems = self.parent.star_map.get_all_systems()
        pr_highlight_list(systems, self.parent.location, "\t<- CURRENT LOCATION")
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
                Command('g', 'Go to jump point', self.outbound_to_jump)
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

        self.parent.location.land()
        self.parent.financials.berthing_fee(self.parent.location.on_surface())
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
        self.parent.location.to_jump_point()
        return cast(ScreenT, Jump(self.parent))

    # ACTIONS ==============================================================

class Starport(Play):
    """Contains commands for the Starport state."""

    def __init__(self, parent: Any) -> None:
        """Create a Starport object."""
        super().__init__(parent)
        self.commands += [
                Command('f', 'Recharge life support', self.recharge),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        cost = self.parent.ship.recharge()
        self.parent.financials.debit(cost)


class Jump(Play):
    """Contains commands for the Jump state."""

    def __init__(self, parent: Any) -> None:
        """Create a Jump object."""
        super().__init__(parent)
        self.commands += [
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================


class Trade(Play):
    """Contains commands for the Trade state."""

    def __init__(self, parent: Any) -> None:
        """Create a Trade object."""
        super().__init__(parent)
        self.commands += [
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================


class Passengers(Play):
    """Contains commands for the Passengers state."""

    def __init__(self, parent: Any) -> None:
        """Create a Passengers object."""
        super().__init__(parent)
        self.commands += [
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================
