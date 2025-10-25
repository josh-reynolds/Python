"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from abc import ABC, abstractmethod
from time import sleep
from typing import Any, List, TypeVar, cast, Tuple
from cargo import Baggage, PassageClass, Passenger
from command import Command
from financials import Credits
from ship import FuelQuality, RepairStatus
from star_system import DeepSpace, StarSystem, Hex
from utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT, confirm_input
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
                Command('r', 'Refuel', self.refuel),
                Command('l', 'Lift off to orbit', self.liftoff),
                Command('t', 'Trade depot', self.to_depot),
                Command('p', 'Passenger terminal', self.to_terminal),
                Command('m', 'Annual maintenance', self.maintenance),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def liftoff(self: ScreenT) -> None | ScreenT:
        """Move from the starport to orbit."""
        print(f"{BOLD_BLUE}Lifting off to orbit {self.parent.location.name}.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot lift off.{END_FORMAT}")
            return None

        # corner case - these messages assume passengers are coming
        # from the current world, which should be true most
        # of the time, but not necessarily all the time
        if self.parent.ship.total_passenger_count > 0:
            print(f"Boarding {self.parent.ship.total_passenger_count} passengers "
                  f"for {self.parent.ship.destination.name}.")

        if self.parent.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.parent.ship.passengers if
                              p.passage == PassageClass.LOW]
            for passenger in low_passengers:
                passenger.guess_survivors(self.parent.ship.low_passenger_count)

        self.parent.location.liftoff()
        return cast(ScreenT, Orbit(self.parent))

    def to_depot(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the trade depot."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} trade depot.{END_FORMAT}")
        self.parent.location.join_trade()
        return cast(ScreenT, Trade(self.parent))

    def to_terminal(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the passenger terminal."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} passenger terminal.{END_FORMAT}")
        self.parent.location.enter_terminal()
        return cast(ScreenT, Passengers(self.parent))

    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        cost = self.parent.ship.recharge()
        self.parent.financials.debit(cost)

    def refuel(self) -> None:
        """Refuel the Ship."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        if self.parent.location.starport in ('E', 'X'):
            print(f"No fuel is available at starport {self.parent.location.starport}.")
            return

        cost = self.parent.ship.refuel(self.parent.location.starport)
        self.parent.financials.debit(cost)

    def maintenance(self) -> None:
        """Perform annual maintenance on the Ship."""
        print(f"{BOLD_BLUE}Performing annual ship maintenance.{END_FORMAT}")
        if self.parent.location.starport not in ('A', 'B'):
            print("Annual maintenance can only be performed at class A or B starports.")
            return

        cost = self.parent.ship.maintenance_cost()
        if self.parent.financials.balance < cost:
            print("You do not have enough funds to pay for maintenance.\n"
                  f"It will cost {cost}. Your balance is {self.parent.financials.balance}.")
            return

        # TO_DO: should we have a confirmation here?
        # TO_DO: should we warn or block if maintenance was performed recently?
        print(f"Performing maintenance. This will take two weeks. Charging {cost}.")
        self.parent.financials.last_maintenance = self.parent.date.current_date
        self.parent.financials.debit(cost)
        self.parent.date.day += 14    # should we wrap this in a method call?
        self.parent.ship.repair_status = RepairStatus.REPAIRED


class Jump(Play):
    """Contains commands for the Jump state."""

    def __init__(self, parent: Any) -> None:
        """Create a Jump object."""
        super().__init__(parent)
        self.commands += [
                Command('i', 'Inbound to orbit', self.inbound_from_jump)
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def inbound_from_jump(self: ScreenT) -> None | ScreenT:
        """Move from the jump point to orbit."""
        if isinstance(self.parent.location, DeepSpace):
            print(f"{BOLD_RED}You are in deep space. "
                  f"There is no inner system to travel to.{END_FORMAT}")
            return None

        print(f"{BOLD_BLUE}Travelling in to orbit {self.parent.location.name}.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot travel to orbit.{END_FORMAT}")
            return None

        leg_fc = self.parent.ship.trip_fuel_cost // 2
        if self.parent.ship.current_fuel < leg_fc:
            print(f"Insufficient fuel. Travel in from the jump point "
                  f"requires {leg_fc} tons, only "
                  f"{self.parent.ship.current_fuel} tons in tanks.")
            return None

        self.parent.ship.current_fuel -= leg_fc
        self.parent.date.day += 1
        self.parent.location.from_jump_point()
        return cast(ScreenT, Orbit(self.parent))

    # ACTIONS ==============================================================


class Trade(Play):
    """Contains commands for the Trade state."""

    def __init__(self, parent: Any) -> None:
        """Create a Trade object."""
        super().__init__(parent)
        self.commands += [
                Command('l', 'Leave trade depot', self.leave_depot),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def leave_depot(self: ScreenT) -> None | ScreenT:
        """Move from the trade depot to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.parent.location.name} trade depot.{END_FORMAT}")
        self.parent.location.leave_trade()
        return cast(ScreenT, Starport(self.parent))

    # ACTIONS ==============================================================


class Passengers(Play):
    """Contains commands for the Passengers state."""

    def __init__(self, parent: Any) -> None:
        """Create a Passengers object."""
        super().__init__(parent)
        self.commands += [
                Command('l', 'Leave terminal', self.leave_terminal),
                Command('b', 'Book passengers', self.book_passengers),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def leave_terminal(self: ScreenT) -> None | ScreenT:
        """Move from the passenger terminal to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.parent.location.name} passenger terminal.{END_FORMAT}")
        self.parent.location.leave_terminal()
        return cast(ScreenT, Starport(self.parent))

    # ACTIONS ==============================================================
    def book_passengers(self) -> None:
        """Book passengers for travel to a destination."""
        print(f"{BOLD_BLUE}Booking passengers.{END_FORMAT}")

        jump_range = self.parent.ship.jump_range
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
