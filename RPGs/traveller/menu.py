"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from time import sleep
from typing import Any, List
from command import Command
from ship import FuelQuality, RepairStatus
from utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT, State
from utilities import YELLOW_ON_RED, BOLD_BLUE, pr_list, pr_highlight_list

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Menu:
    """Draws the menu screen and gathers input from the player."""

    def __init__(self, parent: Any) -> None:
        """Create a Menu object."""
        self.parent = parent
        self.commands: List = [
                Command('n', 'New Game', self.new_game),
                Command('l', 'Load Game', self.load_game),
                Command('q', 'Quit', self.parent.quit)
                ]

    def update(self) -> State:
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

        # duplicates code in Game class, needs refactoring
        # pylint: disable=R0801
        # R0801: Similar lines in 2 files
        command = input("\nEnter a command:  ")
        for cmd in self.commands:
            if command.lower() == cmd.key:
                print()
                cmd.action()
                sleep(1)

        _ = input("Press ENTER key to continue.")
        return State.PLAY

    def new_game(self) -> None:
        """Start a new game."""
        self.parent.ship.name = input("What is the name of your ship? ")

    def load_game(self) -> None:
        """Load a previous game."""

class Play:
    """Draws the play screen and gathers input from the player."""

    def __init__(self, parent: Any) -> None:
        """Create a Menu object."""
        self.parent = parent
        self.commands: List = [
                Command('?', 'List commands', self.list_commands),
                Command('a', 'View star map', self.view_map),
                Command('c', 'Cargo hold contents', self.cargo_hold),
                Command('d', 'Passenger manifest', self.passenger_manifest),
                Command('e', 'Crew roster', self.crew_roster),
                Command('h', 'View ship details', self.view_ship),
                Command('q', 'Quit', self.parent.quit),
                Command('s', 'Save Game', self.save_game),
                Command('v', 'View world characteristics', self.view_world),
                ]

    def update(self) -> State:
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
        command = input("Enter a command (? to list):  ")
        for cmd in self.commands:
            if command.lower() == cmd.key:
                print()
                cmd.action()
                sleep(1)
        return State.PLAY

    def save_game(self) -> None:
        """Save current game state."""
        print(f"{BOLD_BLUE}Saving game.{END_FORMAT}")
        systems = self.parent.star_map.get_all_systems()
        with open('save_game.txt', 'w', encoding='utf-8') as out_file:
            for entry in systems:
                out_file.write(str(entry) + "\n")

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
        """Show the Passenger's booked for transport."""
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
