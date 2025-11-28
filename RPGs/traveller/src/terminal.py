"""Contains the Passengers screen class.

Passengers - contains commands for the Passengers state.
"""
from typing import cast, List, Tuple, Any
from src.baggage import Baggage
from src.command import Command
from src.menu import Play, ScreenT, Starport
from src.passengers import Passenger, PassageClass
from src.star_system import Hex, StarSystem
from src.utilities import BOLD_BLUE, END_FORMAT, BOLD_RED, confirm_input

# TO_DO: ambiguous class name - too close to Passenger - fix this
class Passengers(Play):
    """Contains commands for the Passengers state."""

    def __init__(self, parent: Any) -> None:
        """Create a Passengers object."""
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
        return "Passengers"

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

        jump_range = self.parent.ship.model.jump_range
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
