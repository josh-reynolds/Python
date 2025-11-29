"""Contains the abstract base class for game screens.

Screen - draws the screen and gathers input from the player.
"""
from abc import ABC, abstractmethod
from time import sleep
from typing import Any, List
from src.command import Command
from src.utilities import BOLD_BLUE, END_FORMAT

class Screen(ABC):
    """Base class for game screens."""

    def __init__(self, parent: Any) -> None:
        """Create a Screen object."""
        self.parent = parent
        self.commands: List[Command] = []

    def get_command(self, prompt: str) -> None:
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
    def update(self) -> None:
        """Draw the screen and gather input."""

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def quit(self) -> None:
        """Quit the game."""
        print(f"{BOLD_BLUE}Goodbye.{END_FORMAT}")
        self.parent.running = False

    # ACTIONS ==============================================================
