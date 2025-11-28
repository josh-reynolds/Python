"""Contains the front end menu screen printing and logic.

Menu - draws the screen and gathers input from the player.
"""
from random import randint, choice
from typing import Any, List, cast, Tuple, Dict
from src.baggage import Baggage
from src.cargo import Cargo
from src.cargo_depot import CargoDepot, cargo_hold_from
from src.calendar import modify_calendar_from, Calendar
from src.command import Command
from src.coordinate import Coordinate, coordinate_from, create_3_axis
from src.credits import Credits
from src.financials import financials_from
from src.freight import Freight
from src.orbit import Orbit
from src.passengers import PassageClass, passenger_from
from src.play import Play
from src.terminal import Passengers
from src.screen import ScreenT, Screen
from src.ship import FuelQuality, RepairStatus, ship_from, Ship
from src.ship_model import get_ship_models
from src.star_map import StarMap
from src.star_system import DeepSpace, StarSystem, Hex
from src.star_system_factory import hex_from
from src.subsector import subsector_from
from src.utilities import get_lines, HOME, CLEAR, BOLD_RED, BOLD, END_FORMAT, confirm_input
from src.utilities import BOLD_BLUE, pr_list, die_roll
from src.utilities import get_files, get_json_data
from src.utilities import choose_from

# pylint: disable=C0302
# C0302: Too many lines in module (1078/1000)

class Menu(Screen):
    """Draws the menu screen and gathers input from the player."""

    def __init__(self, parent: Any) -> None:
        """Create a Menu object."""
        super().__init__(parent)
        self.commands: List[Command] = [
                Command('new', 'New Game', self.new_game),
                Command('load', 'Load Game', self.load_game),
                Command('import', 'Import Map Data', self.import_map),
                Command('quit', 'Quit', self.quit),
                ]

    def update(self: ScreenT) -> ScreenT:
        """Draw the screen and present menu choices."""
        # ASCII art from https://patorjk.com/software
        # 'Grafitti' font
        title_lines = get_lines("./data/title.txt")
        string = "Welcome to the Traveller Trading Game!"

        print(f"{HOME}{CLEAR}")
        for line in title_lines:
            line = line.rstrip()
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
    def _load_systems(self, data: List[str]) -> None:
        """Apply StarSystems from json data to Game star_map field."""
        systems = {}
        for line in data:
            map_hex = hex_from(line)
            systems[map_hex.coordinate] = map_hex

        self.parent.star_map = StarMap(systems)

    def _load_subsectors(self, data: List[str]) -> None:
        """Apply Subsectors from json data to Game star_map field."""
        for line in data:
            subsector = subsector_from(line)
            self.parent.star_map.subsectors[subsector.coordinate] = subsector

    def _load_calendar(self, data: str) -> None:
        """Apply date from json data to Game calendar field."""
        self.parent.date = Calendar()
        modify_calendar_from(self.parent.date, data)

    def _load_financials(self, data: str) -> None:
        """Apply Financials from json data to Game financials field."""
        self.parent.financials = financials_from(data)
        self.parent.financials.ship = self.parent.ship
        self.parent.financials.add_observer(self.parent)
        self.parent.date.add_observer(self.parent.financials)

    def _load_location(self, data: str) -> None:
        """Apply location from json data to Game location field."""
        coord = coordinate_from(data)
        location = cast(StarSystem, self.parent.star_map.get_system_at_coordinate(coord))
        self.parent.location = location
        self.parent.location.destinations = self.parent.star_map.get_systems_within_range(
                                                        coord, self.parent.ship.model.jump_range)
        self.parent.financials.location = self.parent.location

    def _create_depot(self) -> None:
        """Create a CargoDepot and apply to Game depot field."""
        self.parent.depot = CargoDepot(self.parent.location, self.parent.date.current_date)
        self.parent.depot.add_observer(self.parent)
        self.parent.depot.controls = self.parent

    def _attach_date_observers(self) -> None:
        """Attach observers to Game date field."""
        self.parent.date.add_observer(self.parent.depot)
        self.parent.date.add_observer(self.parent.financials)

    def _load_screen(self: ScreenT, data: str) -> ScreenT:
        """Apply screen from json data to Game screen field."""
        match data:
            case "Orbit":
                self.parent.location.detail = "orbit"
                return cast(ScreenT, Orbit(self.parent))
            case "Starport":
                self.parent.location.detail = "starport"
                return cast(ScreenT, Starport(self.parent))
            case "Jump":
                self.parent.location.detail = "jump"
                return cast(ScreenT, Jump(self.parent))
            case "Trade":
                self.parent.location.detail = "trade"
                return cast(ScreenT, Trade(self.parent))
            case "Passengers":
                self.parent.location.detail = "terminal"
                return cast(ScreenT, Passengers(self.parent))
            case _:
                raise ValueError(f"unrecognized menu item: '{data}'")

    def _create_empty_hexes(self) -> None:
        """Fill unoccupied hexes in subsectors with DeepSpace."""
        for sub_coord in self.parent.star_map.subsectors:
            occupied = self.parent.star_map.get_systems_in_subsector(sub_coord)
            all_coords = [(i,j) for i in range(1,9) for j in range(1,11)]

            for coord in all_coords:
                converted = create_3_axis(coord[0], coord[1], sub_coord[0], sub_coord[1])

                if converted in occupied:
                    continue
                self.parent.star_map.systems[converted] = DeepSpace(converted)

    def new_game(self: ScreenT) -> ScreenT | None:
        """Start a new game."""
        print(f"{BOLD_BLUE}New game.{END_FORMAT}")
        data = get_json_data("data/new_game.json")
        if not data:
            return None

        # we cast self as ScreenT to allow the polymorphic return
        # value; consequently mypy doesn't recognize methods on self
        self._load_systems(data['systems'])        # type: ignore[attr-defined]
        self._load_subsectors(data['subsectors'])  # type: ignore[attr-defined]
        self._load_calendar(data['date'])          # type: ignore[attr-defined]

        ship_types = get_ship_models()
        model_number = choose_from(ship_types, "\nChoose a ship to start with. ")

        self.parent.ship = Ship(ship_types[model_number])
        self.parent.ship.add_observer(self.parent)
        self.parent.ship.controls = self.parent

        ship_name = ""
        while not ship_name:
            ship_name = input("What is the name of your ship? ")
        self.parent.ship.name = ship_name

        self._load_financials(data['financials'])          # type: ignore[attr-defined]
        self._load_location(data['location'])              # type: ignore[attr-defined]
        self._create_depot()                               # type: ignore[attr-defined]
        self._attach_date_observers()                      # type: ignore[attr-defined]

        _ = input("Press ENTER key to continue.")

        return self._load_screen(data['menu'])             # type: ignore[attr-defined]

    def load_game(self: ScreenT) -> ScreenT | None:
        """Load a previous game."""
        print(f"{BOLD_BLUE}Loading game.{END_FORMAT}")
        files = get_files("./saves/", "json")
        file_number = choose_from(files, "Enter file to load: ")
        load_file = files[file_number]

        data = get_json_data(f"saves/{load_file}")
        if not data:
            return None

        # we cast self as ScreenT to allow the polymorphic return
        # value; consequently mypy doesn't recognize methods on self
        self._load_systems(data['systems'])        # type: ignore[attr-defined]
        self._load_subsectors(data['subsectors'])  # type: ignore[attr-defined]
        self._load_calendar(data['date'])          # type: ignore[attr-defined]

        # all ship components need to be loaded after star systems
        # since we need that list to build destinations

        self.parent.ship = ship_from(data['ship details'], data['ship model'])
        self.parent.ship.add_observer(self.parent)
        self.parent.ship.controls = self.parent

        passengers = []
        for line in data['passengers']:
            passengers.append(passenger_from(line, self.parent.star_map.systems))

        # strictly speaking, this is only necessary if the ship is
        # not on the surface, as it will be re-run on liftoff, and also:
        # TO_DO: duplication of code in liftoff, refactor
        low_passengers = [p for p in self.parent.ship.passengers if
                          p.passage == PassageClass.LOW]
        for passenger in low_passengers:
            passenger.guess_survivors(self.parent.ship.low_passenger_count)
        self.parent.ship.passengers = passengers

        hold_contents = cast(List[Freight | Cargo], cargo_hold_from(data['cargo_hold'],
                                                                    self.parent.star_map.systems))
        self.parent.ship.hold = hold_contents

        destinations = set()
        for passenger in passengers:
            destinations.add(passenger.destination)
        for item in hold_contents:
            if type(item) in [Baggage, Freight]:
                # mypy still checks against Cargo despite the type check
                # since the list is type Sequence[Freight | Cargo]
                destinations.add(item.destination_world)    # type: ignore[union-attr]
        if len(destinations) > 1:
            print(f"{BOLD_RED}Multiple destinations in save file.{END_FORMAT}")
            return None

        self._load_financials(data['financials'])          # type: ignore[attr-defined]
        self.parent.financials.ledger = data['ledger']
        self._load_location(data['location'])              # type: ignore[attr-defined]
        self._create_depot()                               # type: ignore[attr-defined]
        self._attach_date_observers()                      # type: ignore[attr-defined]

        _ = input("Press ENTER key to continue.")

        return self._load_screen(data['menu'])             # type: ignore[attr-defined]

    def _parse_coordinates(self, coord: str) -> Tuple[int, int]:
        r"""Parse a string and extract coordinates from it.

        String is in the format:  (-?\d*,-?\d*)
        This method removes the parentheses, splits on the comma,
        and converts the remaining tokens to integers.
        """
        sub_x, sub_y = coord[1:-1].split(',')
        return (int(sub_x), int(sub_y))

    # pylint: disable=R0912
    # R0912: Too many branches (13/12)
    def _parse_import_file_contents(self,
                                    content: List[str]) -> Dict[str, Dict | List | str] | None:
        """Convert lines from a Traveller map import file into a dictionary.

        The returned dictionary will have three keys: 'subsectors,', 'location' and
        'systems', corresponding to those sections in the file.

        The 'subsectors' key points to a dictionary mapping subsector names
        to their coordinates.

        The 'location' key points to a coordinate on the map (including both
        system coordinate and subsector name).

        The 'systems' key points to a list of star system data in string
        format, one system per line.
        """
        section = ''
        data: Dict[str, Dict | List | str] = {}
        for line in content:
            if len(line) < 2:   # skip blank lines
                continue
            if line[0] == '#':  # skip comments
                continue
            line = line.rstrip()

            if line[0] == '[':
                if line == '[Subsectors]':
                    section = 'subsectors'
                    data[section] = {}
                elif line == '[Systems]':
                    section = 'systems'
                    data[section] = []
                elif line == '[Location]':
                    section = 'location'
                    data[section] = ""
                else:
                    print(f"{BOLD_RED}Unrecognized section header: '{line}'.{END_FORMAT}")
                    return None
                continue

            # data is type Dict[str, Dict | List | str] and mypy
            # can't distinguish the union in the assignments below
            if section == 'subsectors':
                tokens = line.split()
                data[section][tokens[0]] = tokens[1]  # type: ignore[call-overload,index]

            if section == 'systems':
                data[section].append(line)            # type: ignore[union-attr]

            if section == 'location':
                if not data[section]:
                    data[section] = line              # type: ignore[union-attr]
                else:
                    raise ValueError(f"more than one location specified: '{line}'")

        return data

    def _import_systems(self, system_data: List[str], subsector_data: Dict[str,str]) -> List[str]:
        """Convert imported StarSystem data into format used by _load_systems()."""
        system_list = []
        for entry in system_data:
            tokens = entry.split()

            three_axis_coord = self._subsector_coord_to_3_axis(tokens[0], tokens[1],
                                                               subsector_data)
            world_name = tokens[2]
            uwp = tokens[3]

            gas_giant = ""
            if len(tokens) == 5:
                gas_giant = f" - {tokens[4]}"

            world_string = f"{three_axis_coord} - {world_name} - {uwp}{gas_giant}"

            system_list.append(world_string)

        return system_list

    def _import_subsectors(self, subsector_data: Dict[str,str]) -> List[str]:
        """Convert imported Subsector data into format used by _load_systems()."""
        subsector_list = []
        for key, value in subsector_data.items():   # type: ignore[union-attr]
            subsector_list.append(f"{value} - {key}")
        return subsector_list

    def _subsector_coord_to_3_axis(self, subsector_name: str, coord: str,
                                   subsector_data: Dict[str,str]) -> Coordinate:
        """Convert imported Location data into a 3-axis Coordinate."""
        subsector_coord = subsector_data[subsector_name]
        sub_x, sub_y = self._parse_coordinates(subsector_coord) # type: ignore[attr-defined]

        column = int(coord[:2])
        row = int(coord[2:])

        return create_3_axis(column, row, sub_x, sub_y)

    def _import_location(self, subsector_data: Dict[str,str],
                         location_data: str) -> Coordinate:
        """Convert imported Location data into a Coordinate used by _load_systems()."""
        tokens = location_data.split()
        return self._subsector_coord_to_3_axis(tokens[0], tokens[1], subsector_data)

    def _is_star_system(self, coord: Coordinate) -> bool:
        """Test whether a given Coordinate contains a StarSystem or not."""
        return isinstance(self.parent.star_map.systems[coord], StarSystem)

    def import_map(self: ScreenT) -> ScreenT | None:
        """Import Traveller map data and start a new game."""
        print(f"{BOLD_BLUE}Importing data.{END_FORMAT}")
        files = get_files("./import/")
        file_number = choose_from(files, "Enter file to load: ")
        load_file = files[file_number]

        content = get_lines(f"./import/{load_file}")
        data = self._parse_import_file_contents(content)             # type: ignore[attr-defined]

        system_list = self._import_systems(data['systems'],          # type: ignore[attr-defined]
                                           data['subsectors'])
        self._load_systems(system_list)                              # type: ignore[attr-defined]

        subsector_list = self._import_subsectors(data['subsectors']) # type: ignore[attr-defined]
        self._load_subsectors(subsector_list)                        # type: ignore[attr-defined]
        self._create_empty_hexes()                                   # type: ignore[attr-defined]

        # TO_DO: should we interleave with new_game for the remainder? Just
        #        import the map, rest should be the same, right?
        #        or what if we convert the imported data into a new
        #        json file and stash alongside new_game.json?
        self._load_calendar("001-1105")                              # type: ignore[attr-defined]

        ship_types = get_ship_models()
        model_number = choose_from(ship_types, "\nChoose a ship to start with. ")

        self.parent.ship = Ship(ship_types[model_number])
        self.parent.ship.add_observer(self.parent)
        self.parent.ship.controls = self.parent

        ship_name = ""
        while not ship_name:
            ship_name = input("What is the name of your ship? ")
        self.parent.ship.name = ship_name

        financials_string = "10000000 - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        self._load_financials(financials_string)              # type: ignore[attr-defined]
        location = self._import_location(data['subsectors'],  # type: ignore[attr-defined]
                                         data['location'])
        if not self._is_star_system(location):                # type: ignore[attr-defined]
            print(f"{BOLD_RED}The start location in the import file is in Deep Space.{END_FORMAT}")
            return None

        self._load_location(f"{location}")                    # type: ignore[attr-defined]
        self._create_depot()                                  # type: ignore[attr-defined]
        self._attach_date_observers()                         # type: ignore[attr-defined]

        _ = input("\nPress ENTER key to continue.")
        return self._load_screen("Starport")                  # type: ignore[attr-defined]


class Starport(Play):
    """Contains commands for the Starport state."""

    def __init__(self, parent: Any) -> None:
        """Create a Starport object."""
        super().__init__(parent)
        self.commands += [
                Command('life support', 'Recharge life support', self.recharge),
                Command('refuel', 'Refuel', self.refuel),
                Command('liftoff', 'Lift off to orbit', self.liftoff),
                Command('depot', 'Trade depot', self.to_depot),
                Command('terminal', 'Passenger terminal', self.to_terminal),
                Command('maintenance', 'Annual maintenance', self.maintenance),
                Command('flush tanks', 'Flush fuel tanks', self.flush),
                Command('repair', 'Repair ship', self.repair_ship),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __str__(self) -> str:
        """Return the string representation of the current screen."""
        return "Starport"

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

        self.parent.location.detail = "orbit"
        return cast(ScreenT, Orbit(self.parent))

    def to_depot(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the trade depot."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} trade depot.{END_FORMAT}")
        self.parent.location.detail = "trade"
        return cast(ScreenT, Trade(self.parent))

    def to_terminal(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the passenger terminal."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} passenger terminal.{END_FORMAT}")
        self.parent.location.detail = "terminal"
        return cast(ScreenT, Passengers(self.parent))

    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        cost = self.parent.ship.recharge()
        self.parent.financials.debit(cost, "life support")

    def refuel(self) -> None:
        """Refuel the Ship."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        if self.parent.location.starport in ('E', 'X'):
            print(f"No fuel is available at starport {self.parent.location.starport}.")
            return

        cost = self.parent.ship.refuel(self.parent.location.starport)
        self.parent.financials.debit(cost, "refuelling")

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
        self.parent.financials.debit(cost, "annual maintenance")
        self.parent.date.day += 14    # should we wrap this in a method call?
        self.parent.ship.repair_status = RepairStatus.REPAIRED

    def flush(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        print(f"{BOLD_BLUE}Flushing out fuel tanks.{END_FORMAT}")
        if self.parent.ship.fuel_quality == FuelQuality.REFINED:
            print("Ship fuel tanks are clean. No need to flush.")
            return
        if self.parent.location.starport in ('E', 'X'):
            print(f"There are no facilities to flush tanks "
                  f"at starport {self.parent.location.starport}.")
            return

        print("Fuel tanks have been decontaminated.")
        self.parent.ship.fuel_quality = FuelQuality.REFINED
        self.parent.ship.unrefined_jump_counter = 0
        self.parent.date.plus_week()

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self) -> None:
        """Fully repair damage to the Ship (Starport)."""
        print(f"{BOLD_BLUE}Starport repairs.{END_FORMAT}")
        if self.parent.location.starport in ["D", "E", "X"]:
            print(f"No repair facilities available at starport {self.parent.location.starport}")
            return
        if self.parent.ship.repair_status == RepairStatus.REPAIRED:
            print("Your ship is not damaged.")
            return

        print("Your ship is fully repaired and decontaminated.")
        self.parent.ship.repair_status = RepairStatus.REPAIRED
        self.parent.ship.fuel_quality = FuelQuality.REFINED
        self.parent.ship.unrefined_jump_counter = 0
        self.parent.date.plus_week()


class Jump(Play):
    """Contains commands for the Jump state."""

    def __init__(self, parent: Any) -> None:
        """Create a Jump object."""
        super().__init__(parent)
        self.commands += [
                Command('inbound', 'Inbound to orbit', self.inbound_from_jump),
                Command('jump', 'Jump to new system', self.jump),
                Command('skim', 'Skim fuel from gas giant', self.skim),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __str__(self) -> str:
        """Return the string representation of the current screen."""
        return "Jump"

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

        leg_fc = self.parent.ship.model.trip_fuel_cost // 2
        if self.parent.ship.current_fuel < leg_fc:
            print(f"Insufficient fuel. Travel in from the jump point "
                  f"requires {leg_fc} tons, only "
                  f"{self.parent.ship.current_fuel} tons in tanks.")
            return None

        self.parent.ship.current_fuel -= leg_fc
        self.parent.date.day += 1
        self.parent.location.detail = "orbit"
        return cast(ScreenT, Orbit(self.parent))

    # ACTIONS ==============================================================
    def jump(self) -> None:
        """Perform a hyperspace jump to another StarSystem."""
        print(f"{BOLD_BLUE}Preparing for jump.{END_FORMAT}")

        status = self.parent.financials.maintenance_status(self.parent.date.current_date)
        self.parent.ship.check_failure_pre_jump(status)
        if self.parent.ship.repair_status in (RepairStatus.BROKEN, RepairStatus.PATCHED):
            print(f"{BOLD_RED}Drive failure. Cannot perform jump.{END_FORMAT}")
            return

        if not self.parent.ship.sufficient_jump_fuel():
            print(self.parent.ship.insufficient_jump_fuel_message())
            return

        if not self.parent.ship.sufficient_life_support():
            print(self.parent.ship.insufficient_life_support_message())
            return

        jump_range = self.parent.ship.model.jump_range
        print(f"Systems within jump-{jump_range}:")
        destinations = self.parent.location.destinations
        destination_number = choose_from(destinations, "Enter destination number: ")

        coordinate = destinations[destination_number].coordinate
        destination = cast(StarSystem, self.parent.star_map.get_system_at_coordinate(coordinate))

        self.parent.ship.warn_if_not_contracted(destination)

        confirmation = confirm_input(f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling jump.")
            return

        if self.parent.ship.fuel_quality == FuelQuality.UNREFINED:
            self.parent.ship.unrefined_jump_counter += 1

        print(f"{BOLD_RED}Executing jump!{END_FORMAT}")

        self._misjump_check(coordinate)
        self.parent.location.detail = "jump"

        self.parent.ship.check_failure_post_jump()

        coord = self.parent.location.coordinate
        self.parent.location.destinations = self.parent.star_map.get_systems_within_range(coord,
                                                   jump_range)

        self.parent.depot = CargoDepot(self.parent.location, self.parent.date.current_date)
        self.parent.depot.add_observer(self.parent)
        self.parent.depot.controls = self.parent
        self.parent.financials.location = destination

        self.parent.ship.life_support_level = 0
        self.parent.ship.current_fuel -= self.parent.ship.model.jump_fuel_cost
        self.parent.date.plus_week()

    def _misjump_check(self, destination: Coordinate) -> None:
        """Test for misjump and report results."""
        if self.parent.ship.fuel_quality == FuelQuality.UNREFINED:
            modifier = 3
        else:
            modifier = -1
        if self.parent.financials.maintenance_status(self.parent.date.current_date) == "red":
            modifier += 2

        misjump_check = die_roll(2) + modifier
        if misjump_check > 11:
            print(f"{BOLD_RED}MISJUMP!{END_FORMAT}")
            # TO_DO: all this should move to live with the other
            #        three-axis calculations
            distance = randint(1,36)
            hexes = [Coordinate(0,distance,-distance),
                     Coordinate(0,-distance,distance),
                     Coordinate(distance,0,-distance),
                     Coordinate(-distance,0,distance),
                     Coordinate(distance,-distance,0),
                     Coordinate(-distance,distance,0)]
            misjump_target = choice(hexes)
            misjump_target = Coordinate(misjump_target[0] + self.parent.location.coordinate[0],
                                        misjump_target[1] + self.parent.location.coordinate[1],
                                        misjump_target[2] + self.parent.location.coordinate[2])
            print(f"{misjump_target} at distance {distance}")

            # misjump is the only scenario where EmptySpace is a possible
            # location, so we need to leave this type as Hex
            loc = self.parent.star_map.get_system_at_coordinate(misjump_target) # type: ignore
            self.parent.location = loc
            self.parent.star_map.systems[misjump_target] = self.parent.location
        else:
            self.parent.location = cast(StarSystem,
                                        self.parent.star_map.get_system_at_coordinate(destination))

    # Book 2 p. 35
    # Unrefined fuel may be obtained by skimming the atmosphere of a
    # gas giant if unavailable elsewhere. Most star systems have at
    # least one...
    #
    # Traveller '77 does not restrict this to streamlined ships, and
    # also does not include ocean refuelling, but I think I will be
    # including both options. (In all likelihood this will lean heavily
    # toward second edition...)
    def skim(self) -> None:
        """Refuel the Ship by skimming from a gas giant planet."""
        print(f"{BOLD_BLUE}Skimming fuel from a gas giant planet.{END_FORMAT}")
        if not self.parent.location.gas_giant:
            # TO_DO: may want to tweak this message in deep space.
            print("There is no gas giant in this system. No fuel skimming possible.")
            return

        if not self.parent.ship.model.streamlined:
            print("Your ship is not streamlined and cannot skim fuel.")
            return

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")
            return

        if self.parent.ship.current_fuel == self.parent.ship.model.fuel_tank:
            print("Fuel tank is already full.")
            return

        self.parent.ship.current_fuel = self.parent.ship.model.fuel_tank
        self.parent.ship.fuel_quality = FuelQuality.UNREFINED
        self.parent.date.day += 1


class Trade(Play):
    """Contains commands for the Trade state."""

    def __init__(self, parent: Any) -> None:
        """Create a Trade object."""
        super().__init__(parent)
        self.commands += [
                Command('leave', 'Leave trade depot', self.leave_depot),
                Command('buy', 'Buy cargo', self.buy_cargo),
                Command('sell', 'Sell cargo', self.sell_cargo),
                Command('view goods', 'View trade goods', self.goods),
                Command('load freight', 'Load freight', self.load_freight),
                Command('unload freight', 'Unload freight', self.unload_freight),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __str__(self) -> str:
        """Return the string representation of the current screen."""
        return "Trade"

    # VIEW COMMANDS ========================================================
    def goods(self) -> None:
        """Show goods available for purchase."""
        print(f"{BOLD_BLUE}Available cargo loads:{END_FORMAT}")
        pr_list(self.parent.depot.cargo)
        _ = input("\nPress ENTER key to continue.")

    # STATE TRANSITIONS ====================================================
    def leave_depot(self: ScreenT) -> None | ScreenT:
        """Move from the trade depot to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.parent.location.name} trade depot.{END_FORMAT}")
        self.parent.location.detail = "starport"
        return cast(ScreenT, Starport(self.parent))

    # ACTIONS ==============================================================
    def buy_cargo(self) -> None:
        """Purchase cargo for speculative trade."""
        print(f"{BOLD_BLUE}Purchasing cargo.{END_FORMAT}")
        pr_list(self.parent.depot.cargo)
        cargo = self.parent.depot.get_cargo_lot(self.parent.depot.cargo, "buy")
        if cargo is None:
            return

        quantity = self.parent.depot.get_cargo_quantity("buy", cargo)
        if quantity is None:
            return

        if self.parent.depot.insufficient_hold_space(cargo,
                                                     quantity,
                                                     self.parent.ship.free_space()):
            return

        cost = self.parent.depot.determine_price("purchase", cargo, quantity,
                                          self.parent.ship.trade_skill())

        if self.parent.depot.insufficient_funds(cost, self.parent.financials.balance):
            return

        if not self.parent.depot.confirm_transaction("purchase", cargo, quantity, cost):
            return

        self.parent.depot.remove_cargo(self.parent.depot.cargo, cargo, quantity)

        purchased = Cargo(cargo.name, str(quantity), cargo.price, cargo.unit_size,
                          cargo.purchase_dms, cargo.sale_dms, self.parent.location)
        self.parent.ship.load_cargo(purchased)

        self.parent.financials.debit(cost, "cargo purchase")
        self.parent.date.day += 1

    def sell_cargo(self) -> None:
        """Sell cargo in speculative trade."""
        print(f"{BOLD_BLUE}Selling cargo.{END_FORMAT}")
        cargoes = [c for c in self.parent.ship.hold if isinstance(c, Cargo)]

        if len(cargoes) == 0:
            print("You have no cargo on board.")
            return

        pr_list(cargoes)
        cargo = self.parent.depot.get_cargo_lot(cargoes, "sell")
        if cargo is None:
            return

        if self.parent.depot.invalid_cargo_origin(cargo):
            return

        broker_skill = self.parent.depot.get_broker()

        quantity = self.parent.depot.get_cargo_quantity("sell", cargo)
        if quantity is None:
            return

        sale_price = self.parent.depot.determine_price("sale", cargo, quantity,
                                                broker_skill + self.parent.ship.trade_skill())

        self.parent.financials.debit(self.parent.depot.broker_fee(broker_skill, sale_price),
                                     "broker fee")

        if not self.parent.depot.confirm_transaction("sale", cargo, quantity, sale_price):
            return

        self.parent.depot.remove_cargo(self.parent.ship.hold, cargo, quantity)

        self.parent.financials.credit(sale_price, "cargo sale")
        self.parent.date.day += 1

    def load_freight(self) -> None:
        """Select and load Freight onto the Ship."""
        print(f"{BOLD_BLUE}Loading freight.{END_FORMAT}")

        jump_range = self.parent.ship.model.jump_range
        potential_destinations = self.parent.location.destinations.copy()
        destinations = self._get_freight_destinations(potential_destinations, jump_range)
        if not destinations:
            return

        coordinate, available = self.parent.depot.get_available_freight(destinations)
        if available is None:
            return

        destination = cast(StarSystem,
                           self.parent.star_map.get_system_at_coordinate(
                               cast(Coordinate, coordinate)))
        print(f"Freight shipments for {destination.name}")
        print(available)

        total_tonnage, selection = self._select_freight_lots(available, destination)

        if total_tonnage == 0:
            print("No freight shipments selected.")
            return
        print(f"{total_tonnage} tons selected.")

        confirmation = confirm_input(f"Load {total_tonnage} tons of freight? (y/n)? ")
        if confirmation == 'n':
            print("Cancelling freight selection.")
            return

        for entry in selection:
            self.parent.depot.freight[destination].remove(entry)
            self.parent.ship.load_cargo(Freight(entry,
                                         self.parent.location,
                                         destination))
        self.parent.date.day += 1

    def _get_freight_destinations(self, potential_destinations: List[StarSystem],
                                  jump_range: int) -> List[StarSystem]:
        """Return a list of all reachable destinations with Freight lots."""
        result: List[StarSystem] = []
        if self.parent.ship.destination is not None:
            if self.parent.ship.destination == self.parent.location:
                print(f"{BOLD_RED}There is still freight to be unloaded "
                      f"on {self.parent.location.name}.{END_FORMAT}")
                return result
            if self.parent.ship.destination in potential_destinations:
                print("You are under contract. Only showing freight " +
                      f"for {self.parent.ship.destination.name}:\n")
                result = [self.parent.ship.destination]
            else:
                print(f"You are under contract to {self.parent.ship.destination.name} " +
                      "but it is not within jump range of here.")

        else:
            print(f"Available freight shipments within jump-{jump_range}:\n")
            result = potential_destinations

        return result

    def _select_freight_lots(self, available: List[int],
                             destination: Hex) -> Tuple[int, List[int]]:
        """Select Freight lots from a list of available shipments."""
        selection: List[int] = []
        total_tonnage = 0
        hold_tonnage = self.parent.ship.free_space()
        while True:
            if len(available) == 0:
                print(f"No more freight available for {destination.name}.")
                break

            # can't use int input here since we allow for 'q' as well...
            response: int | str = input("Choose a shipment by tonnage ('q' to exit): ")
            if response == 'q':
                break

            try:
                response = int(response)
            except ValueError:
                print("Please input a number.")
                continue

            if response in available:
                if response <= hold_tonnage:
                    # even though we cast to int above in try/catch,
                    # mypy is unaware, need to cast again to silence it.
                    # sort this out...
                    available.remove(cast(int, response))
                    selection.append(cast(int, response))
                    total_tonnage += response
                    hold_tonnage -= response
                    print(available)
                    print(f"Cargo space left: {hold_tonnage}")
                else:
                    print(f"{BOLD_RED}That shipment will not fit in your cargo hold.{END_FORMAT}")
                    print(f"{BOLD_RED}Hold free space: {hold_tonnage}{END_FORMAT}")
            else:
                print(f"{BOLD_RED}There are no shipments of size {response}.{END_FORMAT}")

        print("Done selecting shipments.")
        return (total_tonnage, selection)

    def unload_freight(self) -> None:
        """Unload Freight from the Ship and receive payment."""
        print(f"{BOLD_BLUE}Unloading freight.{END_FORMAT}")

        # truth table: passengers, freight, destination flag,...

        # It should not be possible for there to be freight in the hold,
        # and a destination flag set to None. Should we assert just
        # in case, so we could track down any such bug:
        if self.parent.ship.destination is None:
            print("You have no contracted destination.")
            return

        freight = [f for f in self.parent.ship.hold if isinstance(f, Freight)]
        if len(freight) == 0:
            print("You have no freight on board.")
            return

        if self.parent.ship.destination == self.parent.location:
            freight_tonnage = sum(f.tonnage for f in freight)
            self.parent.ship.hold = [c for c in self.parent.ship.hold if isinstance(c, Cargo)]

            payment = Credits(1000 * freight_tonnage)
            self.parent.financials.credit(Credits(1000 * freight_tonnage), "freight shipment")
            print(f"Receiving payment of {payment} for {freight_tonnage} tons shipped.")

            self.parent.date.day += 1

        else:
            print(f"{BOLD_RED}You are not at the contracted "
                  f"destination for this freight.{END_FORMAT}")
            print(f"{BOLD_RED}It should be unloaded at "
                  f"{self.parent.ship.destination.name}.{END_FORMAT}")
