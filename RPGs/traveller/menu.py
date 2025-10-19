"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT, State

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class Menu:
    """Draws the screen and gathers input from the player."""

    @classmethod
    def update(cls, ship):
        """Draw the screen and present menu choices."""
        # ASCII art from https://patorjk.com/software
        # 'Grafitti' font
        title_lines = get_lines("title.txt")
        string = "Welcome to the Traveller Trading Game!"

        # see wikipedia page for ANSI codes
        print(f"{HOME}{CLEAR}")
        for line in title_lines:
            line = line[:-1]    # strip newline char
            print(f"{BOLD_RED}{line}{END_FORMAT}")
        print(f"{BOLD}\n{string}{END_FORMAT}")

        ship.name = input("What is the name of your ship? ")

        _ = input("Press ENTER key to continue.")
        return State.PLAY
