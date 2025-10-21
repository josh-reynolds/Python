"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from time import sleep
from typing import Any, List
from command import Command
from ship import FuelQuality, RepairStatus
from utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT, State
from utilities import YELLOW_ON_RED

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
                Command('s', 'Save Game', self.save_game),
                Command('q', 'Quit', self.parent.quit)
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
        systems = self.parent.star_map.get_all_systems()
        with open('save_game.txt', 'w', encoding='utf-8') as out_file:
            for entry in systems:
                out_file.write(str(entry) + "\n")
