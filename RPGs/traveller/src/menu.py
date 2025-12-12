"""Contains the front end menu screen printing and logic.

MenuScreen - draws the screen and gathers input from the player.
"""
from typing import Any, List, cast, Tuple, Dict
from src.baggage import Baggage
from src.cargo import Cargo
from src.cargo_depot import CargoDepot, cargo_hold_from
from src.calendar import modify_calendar_from, Calendar
from src.command import Command
from src.coordinate import Coordinate, coordinate_from, create_3_axis
from src.financials import financials_from
from src.format import END_FORMAT, BOLD_BLUE, HOME, CLEAR, BOLD_RED, BOLD
from src.freight import Freight
from src.model import Model
from src.passengers import Passage, passenger_from
from src.screen import Screen
from src.ship import ship_from, Ship
from src.ship_model import get_ship_models
from src.star_map import StarMap
from src.star_system import DeepSpace, StarSystem
from src.star_system_factory import hex_from
from src.subsector import subsector_from
from src.utilities import get_files, get_json_data, choose_from, get_lines

class MenuScreen(Screen):
    """Draws the menu screen and gathers input from the player."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a MenuScreen object."""
        super().__init__(parent, model)
        self.commands: List[Command] = [
                Command('new', 'New Game', self.new_game),
                Command('load', 'Load Game', self.load_game),
                Command('import', 'Import Map Data', self.import_map),
                Command('quit', 'Quit', self.quit),
                ]

    def __repr__(self) -> str:
        """Return the developer string representation of a Menu object."""
        return f"Menu({self.parent!r})"

    def _print_title(self) -> None:
        """Draw the game title."""
        # ASCII art from https://patorjk.com/software
        # 'Grafitti' font
        title_lines = get_lines("./data/title.txt")
        string = "Welcome to the Traveller Trading Game!"

        print(f"{HOME}{CLEAR}")
        for line in title_lines:
            line = line.rstrip()
            print(f"{BOLD_RED}{line}{END_FORMAT}")
        print(f"{BOLD}\n{string}{END_FORMAT}")

    def _get_menu_choice(self):
        """Take player's choice from the menu."""
        for command in self.commands:
            print(f"{command.key} - {command.description}")

        self.get_command("\nEnter a command:  ")

    def update(self) -> None:
        """Draw the screen and present menu choices."""
        self._print_title()
        self._get_menu_choice()

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================
    def _load_systems(self, data: List[str]) -> None:
        """Apply StarSystems from json data to Game star_map field."""
        systems = {}
        for line in data:
            map_hex = hex_from(line)
            systems[map_hex.coordinate] = map_hex

        self.model.star_map = StarMap(systems)

    def _load_subsectors(self, data: List[str]) -> None:
        """Apply Subsectors from json data to Game star_map field."""
        for line in data:
            subsector = subsector_from(line)
            self.model.star_map.subsectors[subsector.coordinate] = subsector

    def _load_calendar(self, data: str) -> None:
        """Apply date from json data to Game calendar field."""
        self.model.date = Calendar()
        modify_calendar_from(self.model.date, data)

    def _load_financials(self, data: str) -> None:
        """Apply Financials from json data to Game financials field."""
        self.model.financials = financials_from(data)
        self.model.financials.ship = self.model.ship
        self.model.financials.add_observer(self.parent)
        self.model.date.add_observer(self.model.financials)

    def _load_location(self, data: str) -> None:
        """Apply location from json data to Game location field."""
        coord = coordinate_from(data)
        location = cast(StarSystem, self.model.get_system_at_coordinate(coord))
        self.model.location = location
        self.model.location.destinations = \
                self.model.star_map.get_systems_within_range(coord,
                                                        self.model.ship.model.jump_range)
        self.model.financials.location = self.model.location

    def _create_depot(self) -> None:
        """Create a CargoDepot and apply to Game depot field."""
        self.model.depot = CargoDepot(self.model.location,
                                       self.model.get_current_date())
        self.model.depot.add_observer(self.parent)
        self.model.depot.controls = self.parent

    def _attach_date_observers(self) -> None:
        """Attach observers to Game date field."""
        self.model.date.add_observer(self.model.depot)
        self.model.date.add_observer(self.model.financials)

    def _create_empty_hexes(self) -> None:
        """Fill unoccupied hexes in subsectors with DeepSpace."""
        for sub_coord in self.model.star_map.subsectors:
            occupied = self.model.star_map.get_systems_in_subsector(sub_coord)
            all_coords = [(i,j) for i in range(1,9) for j in range(1,11)]

            for coord in all_coords:
                converted = create_3_axis(coord[0], coord[1], sub_coord[0], sub_coord[1])

                if converted in occupied:
                    continue
                self.model.star_map.systems[converted] = DeepSpace(converted)

    def new_game(self) -> None:
        """Start a new game."""
        print(f"{BOLD_BLUE}New game.{END_FORMAT}")
        data = get_json_data("data/new_game.json")
        if not data:
            return None

        self._load_systems(data['systems'])
        self._load_subsectors(data['subsectors'])
        self._load_calendar(data['date'])

        ship_types = get_ship_models()
        model_number = choose_from(ship_types, "\nChoose a ship to start with. ")

        self.model.ship = Ship(ship_types[model_number])
        self.model.ship.add_observer(self.parent)
        self.model.ship.controls = self.parent

        ship_name = ""
        while not ship_name:
            ship_name = input("What is the name of your ship? ")
        self.model.ship.name = ship_name

        self._load_financials(data['financials'])
        self._load_location(data['location'])
        self._create_depot()
        self._attach_date_observers()

        _ = input("Press ENTER key to continue.")

        self.model.set_location(data['menu'].lower())
        self.parent.change_state(data['menu'])
        return None

    def load_game(self) -> None:
        """Load a previous game."""
        print(f"{BOLD_BLUE}Loading game.{END_FORMAT}")
        files = get_files("./saves/", "json")
        file_number = choose_from(files, "Enter file to load: ")
        load_file = files[file_number]

        data = get_json_data(f"saves/{load_file}")
        if not data:
            return None

        self._load_systems(data['systems'])
        self._load_subsectors(data['subsectors'])
        self._load_calendar(data['date'])

        # all ship components need to be loaded after star systems
        # since we need that list to build destinations

        self.model.ship = ship_from(data['ship details'], data['ship model'])
        self.model.ship.add_observer(self.parent)
        self.model.ship.controls = self.parent

        passengers = []
        for line in data['passengers']:
            passengers.append(passenger_from(line, self.model.star_map.systems))

        # strictly speaking, this is only necessary if the ship is
        # not on the surface, as it will be re-run on liftoff, and also:
        # TO_DO: duplication of code in liftoff, refactor
        low_passengers = [p for p in passengers if
                          p.passage == Passage.LOW]
        for passenger in low_passengers:
            passenger.guess_survivors(self.model.low_passenger_count)
        self.model.set_passengers(passengers)

        hold_contents = cast(List[Freight | Cargo], cargo_hold_from(data['cargo_hold'],
                                                      self.model.star_map.systems))
        self.model.ship.hold = hold_contents

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

        self._load_financials(data['financials'])
        self.model.financials.ledger = data['ledger']
        self._load_location(data['location'])
        self._create_depot()
        self._attach_date_observers()

        _ = input("Press ENTER key to continue.")
        self.model.set_location(data['menu'].lower())
        self.parent.change_state(data['menu'])
        return None

    def _parse_coordinates(self, coord: str) -> Tuple[int, int]:
        r"""Parse a string and extract coordinates from it.

        String is in the format:  (-?\d*,-?\d*)
        This method removes the parentheses, splits on the comma,
        and converts the remaining tokens to integers.
        """
        sub_x, sub_y = coord[1:-1].split(',')
        return (int(sub_x), int(sub_y))

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
            if len(line) < 2 or line[0] == '#':   # skip blank lines & comments
                continue
            line = line.rstrip()

            if line[0] == '[':
                match line:
                    case '[Subsectors]':
                        section = 'subsectors'
                        data[section] = {}
                    case '[Systems]':
                        section = 'systems'
                        data[section] = []
                    case '[Location]':
                        section = 'location'
                        data[section] = ""
                    case _:
                        print(f"{BOLD_RED}Unrecognized section header: '{line}'.{END_FORMAT}")
                        return None
                continue

            # data is type Dict[str, Dict | List | str] and mypy
            # can't distinguish the union in the assignments below
            match section:
                case 'subsectors':
                    tokens = line.split()
                    data[section][tokens[0]] = tokens[1]  # type: ignore[call-overload,index]
                case 'systems':
                    data[section].append(line)            # type: ignore[union-attr]
                case 'location':
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
        sub_x, sub_y = self._parse_coordinates(subsector_coord)

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
        return isinstance(self.model.star_map.systems[coord], StarSystem)

    def import_map(self) -> None:
        """Import Traveller map data and start a new game."""
        print(f"{BOLD_BLUE}Importing data.{END_FORMAT}")
        files = get_files("./import/")
        file_number = choose_from(files, "Enter file to load: ")
        load_file = files[file_number]

        content = get_lines(f"./import/{load_file}")
        data = self._parse_import_file_contents(content)

        system_list = self._import_systems(data['systems'],          # type: ignore[index, arg-type]
                                           data['subsectors'])       # type: ignore[index, arg-type]
        self._load_systems(system_list)

        subsector_list = self._import_subsectors(data['subsectors']) # type: ignore[index, arg-type]
        self._load_subsectors(subsector_list)
        self._create_empty_hexes()

        # TO_DO: should we interleave with new_game for the remainder? Just
        #        import the map, rest should be the same, right?
        #        or what if we convert the imported data into a new
        #        json file and stash alongside new_game.json?
        self._load_calendar("001-1105")

        ship_types = get_ship_models()
        model_number = choose_from(ship_types, "\nChoose a ship to start with. ")

        self.model.ship = Ship(ship_types[model_number])
        self.model.ship.add_observer(self.parent)
        self.model.ship.controls = self.parent

        ship_name = ""
        while not ship_name:
            ship_name = input("What is the name of your ship? ")
        self.model.ship.name = ship_name

        financials_string = "10000000 - 001-1105 - 001-1105 - 001-1105 - 001-1105 - 352-1104"
        self._load_financials(financials_string)
        location = self._import_location(data['subsectors'],  # type: ignore[index, arg-type]
                                         data['location'])    # type: ignore[index, arg-type]
        if not self._is_star_system(location):
            print(f"{BOLD_RED}The start location in the import file is in Deep Space.{END_FORMAT}")
            return None

        self._load_location(f"{location}")
        self._create_depot()
        self._attach_date_observers()

        _ = input("\nPress ENTER key to continue.")
        self.model.set_location("starport")
        self.parent.change_state("Starport")
        return None
