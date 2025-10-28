"""Contains the game loop and game logic for a Traveller trading simulation.

Game - contains the game loop and basic controller/view logic.
"""
from typing import cast
from calendar import Calendar
from coordinate import Coordinate
from financials import Financials, Credits
from menu import Menu
from utilities import int_input, confirm_input
from utilities import BOLD_YELLOW, BOLD_RED, END_FORMAT, BOLD_GREEN
from ship import Ship
from cargo import Cargo, CargoDepot
from star_system import DeepSpace, StarSystem
from star_map import StarMap, StarSystemFactory, Subsector

# pylint: disable=R0902
# R0902: Too many instance attributes (8/7)
class Game:
    """Contains the game loop and basic congtroller/view logic."""

    def __init__(self) -> None:
        """Create an instance of Game."""
        self.running = False
        self.screen = Menu(self)
        self.date = Calendar()

        self.ship = Ship()
        self.ship.load_cargo(Cargo("Grain", '20', Credits(300), 1,
                                   {"Ag":-2,"Na":1,"In":2},
                                   {"Ag":-2}))

        self.star_map = StarMap({
            Coordinate(0,0,0)  : StarSystemFactory.create("Yorbund",
                                                          Coordinate(0,0,0),
                                                          "A", 8, 7, 5, 9, 5, 5, 10),
            Coordinate(0,1,-1) : DeepSpace(Coordinate(0,1,-1)),
            Coordinate(0,-1,1) : StarSystemFactory.create("Mithril",
                                                          Coordinate(0,-1,1),
                                                          "A", 8, 4, 0, 7, 5, 5, 10),
            Coordinate(1,0,-1) : StarSystemFactory.create("Kinorb",
                                                          Coordinate(1,0,-1),
                                                          "A", 8, 5, 5, 7, 5, 5, 10),
            Coordinate(-1,0,1) : DeepSpace(Coordinate(-1,0,1)),
            Coordinate(1,-1,0) : DeepSpace(Coordinate(1,-1,0)),
            Coordinate(-1,1,0) : StarSystemFactory.create("Aramis",
                                                          Coordinate(-1,1,0),
                                                          "A", 8, 6, 5, 8, 5, 5, 10)
            })
        self.star_map.subsectors[(0,0)] = Subsector("Regina", (0,0))

        self.location = cast(StarSystem, self.star_map.get_system_at_coordinate(Coordinate(0,0,0)))
        coord = self.location.coordinate
        self.location.destinations = self.star_map.get_systems_within_range(coord,
                                                              self.ship.jump_range)
        self.financials = Financials(10000000, self.date.current_date, self.ship, self.location)
        self.depot = CargoDepot(self.location, self.date.current_date)

        self.ship.add_observer(self)
        self.ship.controls = self
        self.depot.add_observer(self)
        self.depot.controls = self
        self.financials.add_observer(self)

        self.date.add_observer(self.depot)
        self.date.add_observer(self.financials)

    def on_notify(self, message: str, priority: str = "") -> None:
        """Print messages received from model objects."""
        fmt = ""
        end = END_FORMAT
        if priority == "green":
            fmt = BOLD_GREEN
        elif priority == "yellow":
            fmt = BOLD_YELLOW
        elif priority == "red":
            fmt = BOLD_RED
        else:
            end = ""

        print(fmt + message + end)

    def get_input(self, constraint: str, prompt: str) -> str | int:
        """Get input from the player and return results to the model class."""
        if constraint == 'confirm':
            result: str | int = confirm_input(prompt)
        elif constraint == 'int':
            result = int_input(prompt)
        else:
            result = input(prompt)
        return result

    def run(self) -> None:
        """Run the game loop."""
        self.running = True
        while self.running:
            self.screen = self.screen.update()

if __name__ == '__main__':
    Game().run()
