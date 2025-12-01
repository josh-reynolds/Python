"""Contains the base class for play screens.

Screen - draws the play screen and gathers input from the player.
"""
import json
from fnmatch import fnmatch
from os import listdir
from typing import Any, List
from src.command import Command
from src.coordinate import absolute
from src.draw_map import draw_map
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED, BOLD_GREEN, CLEAR, YELLOW_ON_RED, HOME
from src.screen import Screen
from src.ship import FuelQuality, RepairStatus
from src.star_system import StarSystem
from src.utilities import choose_from, pr_list, pr_highlight_list
from src.utilities import get_next_file, die_roll, confirm_input

class Play(Screen):
    """Draws the play screen and gathers input from the player.

    Base class for all Play screens.
    """

    def __init__(self, parent: Any) -> None:
        """Create a Play Screen object."""
        super().__init__(parent)
        self.commands: List[Command] = [
                Command('?', 'List commands', self.list_commands),
                Command('map', 'View star map', self.view_map),
                Command('cargo', 'Cargo hold contents', self.cargo_hold),
                Command('passengers', 'Passenger manifest', self.passenger_manifest),
                Command('crew', 'Crew roster', self.crew_roster),
                Command('ship', 'View ship details', self.view_ship),
                Command('damage control', 'Engineering damage control', self.damage_control),
                Command('quit', 'Quit', self.quit),
                Command('world', 'View world characteristics', self.view_world),
                Command('wait', 'Wait a week', self.wait_week),
                Command('save', 'Save Game', self.save_game),
                Command('ledger', 'View ledger', self.view_ledger),
                Command('dump map', 'Dump map', self.dump_map),
                Command('dump ledger', 'Dump ledger', self.dump_ledger),
                Command('draw map', 'Create map image', self.draw_map),
                ]

    def update(self) -> None:
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

        fuel_amount = f"{self.parent.ship.current_fuel}/{self.parent.ship.model.fuel_tank}"

        print(f"{HOME}{CLEAR}")
        print(f"{YELLOW_ON_RED}\n{self.parent.date} : You are " +
              f"{self.parent.location.description()}.{repair_state}{END_FORMAT}")
        print(f"Credits: {self.parent.financials.balance}"
              f"\tFree hold space: {self.parent.ship.free_space()} tons"
              f"\tFuel: {fuel_amount} tons {fuel_quality}"
              f"\tLife support: {self.parent.ship.life_support_level}%")

        self.get_command("Enter a command (? to list):  ")

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
        coord = self.parent.location.coordinate.trav_coord
        sub_string = self.parent.star_map.pretty_coordinates(coord)
        print(f"{sub_string} : {self.parent.location}")
        _ = input("\nPress ENTER key to continue.")

    def view_ledger(self) -> None:
        """View the bank transaction ledger."""
        print(f"{BOLD_BLUE}Financial transactions:{END_FORMAT}")
        print("DATE\t\t - DEBIT\t - CREDIT\t - BALANCE\t - SYSTEM\t - MEMO")
        transactions = self.parent.financials.ledger
        for transaction in transactions:
            print(transaction)
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

    # TO_DO: some duplication with view_world() - refactor
    def view_map(self) -> None:
        """View all known StarSystems."""
        print(f"{BOLD_BLUE}All known star systems:{END_FORMAT}")
        systems = self.parent.star_map.get_all_systems()
        system_strings = []
        highlight = ""
        for sys in systems:
            coord = sys.coordinate.trav_coord
            sub_string = self.parent.star_map.pretty_coordinates(coord)
            combined = f"{sub_string} : {sys}"
            system_strings.append(combined)
            if sys == self.parent.location:
                highlight = combined
        pr_highlight_list(system_strings, highlight, "\t<- CURRENT LOCATION")
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

    # pylint: disable=R0914
    # R0914: Too many local variables(16/15)
    def save_game(self) -> None:
        """Save current game state."""
        print(f"{BOLD_BLUE}Saving game.{END_FORMAT}")
        systems = []
        for coord in self.parent.star_map.systems:
            map_hex = self.parent.star_map.systems[coord]
            systems.append(f"{coord} - {map_hex}")

        subsectors = []
        for coord in self.parent.star_map.subsectors:
            sub = self.parent.star_map.subsectors[coord]
            subsectors.append(f"{coord} - {sub}")

        date_string = f"{self.parent.date}"

        ship_model_string = self.parent.ship.model.name
        ship_string = self.parent.ship.encode()

        passenger_list = [p.encode() for p in self.parent.ship.passengers]

        cargo_hold_list = [p.encode() for p in self.parent.ship.hold]

        financials_string = self.parent.financials.encode()

        location_string = f"{self.parent.location.coordinate}"

        menu_string = f"{self.parent.screen}"

        save_data = {
                     'date' : date_string,
                     'systems' : systems,
                     'subsectors' : subsectors,
                     'location' : location_string,
                     'menu' : menu_string,
                     'ship model' : ship_model_string,
                     'ship details' : ship_string,
                     'passengers' : passenger_list,
                     'cargo_hold' : cargo_hold_list,
                     'financials' : financials_string,
                     'ledger' : self.parent.financials.ledger
                     }

        filename = get_next_file("save_game", "json")
        with open(f"saves/{filename}", 'w', encoding='utf-8') as a_file:
            json.dump(save_data, a_file, indent=2)
        print(f"{BOLD_GREEN}Saved to {filename}.{END_FORMAT}")

    def wait_week(self) -> None:
        """Advance the Calendar by seven days."""
        print(f"{BOLD_BLUE}Waiting.{END_FORMAT}")
        self.parent.date.plus_week()

    def dump_map(self) -> None:
        """Output the map data to a file in a human-readable format."""
        print(f"{BOLD_BLUE}Dumping map data.{END_FORMAT}")
        for file in listdir():
            if fnmatch(file, "star_map.txt"):
                confirmation = confirm_input("Star map file already exists. Continue (y/n)? ")
                if confirmation == "n":
                    return

        # working this out here, but should move to star_map and/or coordinate eventually
        star_map = self.parent.star_map
        system_list = []
        for system in star_map.systems.items():
            coord = absolute(system[0])
            coord_string = star_map.pretty_coordinates(coord)
            system_list.append(f"{coord[1]} : {coord_string} : {system[1]}\n")
        system_list.sort()

        with open("star_map.txt", "w", encoding="utf-8") as a_file:
            for line in system_list:
                a_file.write(line)


    def dump_ledger(self) -> None:
        """Output the ledger data to a file in a human-readable format."""
        print(f"{BOLD_BLUE}Dumping ledger data.{END_FORMAT}")
        for file in listdir():
            if fnmatch(file, "ledger.txt"):
                confirmation = confirm_input("Ledger file already exists. Continue (y/n)? ")
                if confirmation == "n":
                    return

        ledger = self.parent.financials.ledger
        if len(ledger) == 0:
            print(f"{BOLD_RED}There are no ledger entries to write.{END_FORMAT}")
            return
        text = "\n".join(ledger) + "\n"

        with open("ledger.txt", "w", encoding="utf-8") as a_file:
            a_file.write("DATE\t\t - DEBIT\t - CREDIT\t - BALANCE\t - SYSTEM\t - MEMO\n")
            a_file.write(text)

    def draw_map(self) -> None:
        """Create and save a bitmap file of the current map."""
        print(f"{BOLD_BLUE}Creating map image.{END_FORMAT}")
        sub_list = list(self.parent.star_map.subsectors.items())
        subsector = choose_from(sub_list, "Choose a subsector to draw: ")
        sub_coord = sub_list[subsector][0]
        sub_name = sub_list[subsector][1].name

        color_schemes = ["Light", "Dark"]
        color_choice = choose_from(color_schemes, "Choose a color scheme: ")
        print_friendly = color_choice == 0

        system_coords = self.parent.star_map.get_systems_in_subsector(sub_coord)
        system_list = []
        for entry in system_coords:
            system_list.append(self.parent.star_map.systems[entry])

        draw_map(system_list, sub_name, print_friendly)

    def _get_destinations(self, potential_destinations: List[StarSystem],
                           jump_range: int, prompt: str) -> List[StarSystem]:
        """Return a list of all reachable destinations with Freight or Passengers."""
        result: List[StarSystem] = []
        if self.parent.ship.destination is not None:
            if self.parent.ship.destination == self.parent.location:
                print(f"{BOLD_RED}There is still freight to be unloaded "
                      f"on {self.parent.location.name}.{END_FORMAT}")
                return result
            if self.parent.ship.destination in potential_destinations:
                print(f"You are under contract. Only showing {prompt} " +
                      f"for {self.parent.ship.destination.name}:\n")
                result = [self.parent.ship.destination]
            else:
                print(f"You are under contract to {self.parent.ship.destination.name} " +
                      "but it is not within jump range of here.")

        else:
            print(f"Available {prompt} within jump-{jump_range}:\n")
            result = potential_destinations

        return result

    def _check_fuel_level(self, prompt: str) -> int | None:
        """Verify there is sufficient fuel in the tanks to make a trip."""
        leg_fc = self.parent.ship.model.trip_fuel_cost // 2
        if self.parent.ship.current_fuel < leg_fc:
            print(f"Insufficient fuel. Travel {prompt} the jump point "
                  f"requires {leg_fc} tons, only "
                  f"{self.parent.ship.current_fuel} tons in tanks.")
            return None
        return leg_fc
