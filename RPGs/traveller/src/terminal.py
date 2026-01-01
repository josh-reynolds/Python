"""Contains the TerminalScreen class.

TerminalScreen - contains commands for the terminal state.
"""
from typing import cast, Any
from src.baggage import Baggage
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model
from src.passengers import Passenger, Passage
from src.play import PlayScreen
from src.star_system import StarSystem
from src.utilities import confirm_input

class TerminalScreen(PlayScreen):
    """Contains commands for the terminal state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a TerminalScreen object."""
        super().__init__(parent, model)

        # this is declared as List[Command] in super(),
        # but mypy still cannot determine type
        self.commands += [                        # type: ignore[has-type]
                Command('leave', 'Leave terminal', self.leave_terminal),
                Command('book', 'Book passengers', self.book_passengers),
                ]
        self.commands = sorted(self.commands,     # type: ignore[has-type]
                               key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Terminal({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def leave_terminal(self) -> None:
        """Move from the passenger terminal to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.model.system_name()} " +
              f"passenger terminal.{END_FORMAT}")
        print(self.model.to_starport())
        self.parent.change_state("Starport")

    # ACTIONS ==============================================================
    def book_passengers(self) -> None:
        """Book passengers for travel to a destination."""
        print(f"{BOLD_BLUE}Booking passengers.{END_FORMAT}")

        jump_range = self.model.jump_range
        potential_destinations = self.model.destinations
        destinations = self.model.get_destinations(potential_destinations,
                                              jump_range, "passengers")
        if not destinations:
            return

        coordinate, available = self.model.get_available_passengers(destinations)
        if available is None:
            return

        destination = cast(StarSystem,
                           self.model.get_system_at_coordinate(coordinate))
        print(f"Passengers for {destination.name} (H,M,L): {available}")

        selection = self.model.select_passengers(available, destination)

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
        high = [Passenger(Passage.HIGH, destination)
                for _ in range(selection[Passage.HIGH.value])]
        baggage = [Baggage(self.model.get_star_system(), destination)
                   for _ in range(selection[Passage.HIGH.value])]
        middle = [Passenger(Passage.MIDDLE, destination)
                  for _ in range(selection[Passage.MIDDLE.value])]
        low = [Passenger(Passage.LOW, destination)
               for _ in range(selection[Passage.LOW.value])]

        self.model.add_passengers(high)
        self.model.load_cargo(baggage)        #type: ignore[arg-type]
        self.model.add_passengers(middle)
        self.model.add_passengers(low)
        self.model.remove_passengers_from_depot(destination, selection)
