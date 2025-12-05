"""Contains the TerminalScreen class.

TerminalScreen - contains commands for the terminal state.
"""
from typing import cast, Tuple, Any, List
from src.baggage import Baggage
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.passengers import Passenger, Passage
from src.play import PlayScreen
from src.star_system import Hex, StarSystem
from src.utilities import confirm_input, get_plural_suffix

class TerminalScreen(PlayScreen):
    """Contains commands for the terminal state."""

    def __init__(self, parent: Any) -> None:
        """Create a TerminalScreen object."""
        super().__init__(parent)

        # this is declared as List[Command] in super(),
        # but mypy still cannot determine type
        self.commands += [                        # type: ignore[has-type]
                Command('leave', 'Leave terminal', self.leave_terminal),
                Command('book', 'Book passengers', self.book_passengers),
                ]
        self.commands = sorted(self.commands,     # type: ignore[has-type]
                               key=lambda command: command.key)

    def __str__(self) -> str:
        """Return the string representation of the current screen."""
        return "Terminal"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def leave_terminal(self) -> None:
        """Move from the passenger terminal to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.parent.location.name} passenger terminal.{END_FORMAT}")
        self.parent.change_state("Starport")

    # ACTIONS ==============================================================
    def book_passengers(self) -> None:
        """Book passengers for travel to a destination."""
        print(f"{BOLD_BLUE}Booking passengers.{END_FORMAT}")

        jump_range = self.parent.ship.model.jump_range
        potential_destinations = self.parent.location.destinations.copy()
        destinations = self._get_destinations(potential_destinations,
                                              jump_range, "passengers")
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
        high = [Passenger(Passage.HIGH, destination)
                for _ in range(selection[Passage.HIGH.value])]
        baggage = [Baggage(self.parent.location, destination)
                   for _ in range(selection[Passage.HIGH.value])]
        middle = [Passenger(Passage.MIDDLE, destination)
                  for _ in range(selection[Passage.MIDDLE.value])]
        low = [Passenger(Passage.LOW, destination)
               for _ in range(selection[Passage.LOW.value])]

        self.parent.ship.passengers += high
        self.parent.ship.hold += baggage
        self.parent.ship.passengers += middle
        self.parent.ship.passengers += low
        self.parent.depot.passengers[destination] = tuple(a-b for a,b in
                                                   zip(self.parent.depot.passengers[destination],
                                                       selection))

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

            tokens = response.split()
            count, passage = _valid_input(tokens)
            if not count:
                continue

            suffix = get_plural_suffix(count)

            # pylint: disable=E1130
            # E1130: bad operand type for unary-: NoneType
            match passage:
                case 'h':
                    if not _sufficient_quantity("high", available[0],
                                                ship_capacity[0], count, ship_hold):
                        continue
                    print(f"Adding {count} high passenger{suffix}.")
                    selection = tuple(a+b for a,b in zip(selection,(count,0,0)))
                    available = tuple(a+b for a,b in zip(available,(-count,0,0)))
                    ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-count,0)))
                    ship_hold -= count

                case 'm':
                    if not _sufficient_quantity("middle", available[1],
                                                ship_capacity[0], count, ship_hold):
                        continue
                    print(f"Adding {count} middle passenger{suffix}.")
                    selection = tuple(a+b for a,b in zip(selection,(0,count,0)))
                    available = tuple(a+b for a,b in zip(available,(0,-count,0)))
                    ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-count,0)))

                case 'l':
                    if not _sufficient_quantity("low", available[2],
                                                ship_capacity[1], count, ship_hold):
                        continue
                    print(f"Adding {count} low passenger{suffix}.")
                    selection = tuple(a+b for a,b in zip(selection,(0,0,count)))
                    available = tuple(a+b for a,b in zip(available,(0,0,-count)))
                    ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(0,-count)))

            print()
            print(f"Remaining (H, M, L): {available}")
            print(f"Selected (H, M, L): {selection}")
            print(f"Empty ship berths (H+M, L): {ship_capacity}\n")

        print("Done selecting passengers.")
        return selection

def _sufficient_quantity(passage: str, available: int,
                         capacity: int, count: int, hold: int) -> bool:
    """Test whether there are enough berths/passengers to book."""
    if available - count < 0:
        print(f"There are not enough {passage} passengers available.")
        return False

    if capacity - count < 0:
        berths = "staterooms"
        if passage == "low":
            berths = "low berths"
        print(f"There are not enough {berths} available.")
        return False

    if passage == "high":
        if hold - count < 0:
            print("There is not enough cargo space available.")
            return False

    return True

def _valid_input(tokens: List[str]) -> Tuple[int | None, str | None]:
    """Validate passenger selection input."""
    if len(tokens) != 2:
        print("Please enter in the format: passage number (example: h 5).")
        return None, None

    passage = tokens[0]
    if passage not in ['h', 'm', 'l']:
        print("Please enter 'h', 'm' or 'l' for passage class.")
        return None, None

    try:
        count = int(tokens[1])
    except ValueError:
        print("Please input a number.")
        return None, None

    return count, passage
