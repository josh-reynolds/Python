"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from time import sleep
from typing import Any, List
from command import Command
from utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT, State

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Menu:
    """Draws the screen and gathers input from the player."""

    def __init__(self, parent: Any) -> None:
        """Create a Menu object."""
        self.parent = parent
        self.commands: List = [
                Command('n', 'New Game', self.new_game),
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
