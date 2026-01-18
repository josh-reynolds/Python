"""Contains the TerminalScreen class.

TerminalScreen - contains commands for the terminal state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen

class TerminalScreen(PlayScreen):
    """Contains commands for the terminal state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a TerminalScreen object."""
        super().__init__(parent, model)

        # this is declared as List[Command] in super(),
        # but mypy still cannot determine type
        self.commands += [                        # type: ignore[has-type]
                Command('leave', 'Leave terminal', self.to_downport),
                Command('book', 'Book passengers', self.book_passengers),
                ]
        self.commands = sorted(self.commands,     # type: ignore[has-type]
                               key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Terminal({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def to_downport(self) -> None:
        """Move from the passenger terminal to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.model.system_name()} " +
              f"passenger terminal.{END_FORMAT}")
        print(self.model.to_starport())
        self.parent.change_state("Starport")

    # ACTIONS ==============================================================
    def book_passengers(self) -> None:
        """Book passengers for travel to a destination."""
        print(f"{BOLD_BLUE}Booking passengers.{END_FORMAT}")
        try:
            print(self.model.book_passengers())
        except GuardClauseFailure as exception:
            print(exception)
