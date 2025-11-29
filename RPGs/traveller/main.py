"""Contains the game loop and game logic for a Traveller trading simulation.

Game - contains the game loop and basic controller/view logic.
"""
from src.calendar import Calendar
from src.cargo_depot import CargoDepot
from src.financials import Financials
from src.jump import Jump
from src.menu import Menu
from src.orbit import Orbit
from src.screen import Screen
from src.ship import Ship
from src.star_system import StarSystem
from src.star_map import StarMap
from src.starport import Starport
from src.terminal import Passengers
from src.trade import Trade
from src.utilities import int_input, confirm_input
from src.utilities import BOLD_YELLOW, BOLD_RED, END_FORMAT, BOLD_GREEN

# pylint: disable=R0902
# R0902: Too many instance attributes (8/7)
class Game:
    """Contains the game loop and basic controller/view logic."""

    def __init__(self) -> None:
        """Create an instance of Game."""
        self.running = False
        self.screen: Screen = Menu(self)

        self.date: Calendar
        self.ship: Ship
        self.star_map: StarMap
        self.location: StarSystem
        self.financials: Financials
        self.depot: CargoDepot

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
            self.screen.update()

    def change_state(self, new_state) -> None:
        """Change game screens."""
        match new_state:
            case "Orbit":
                self.location.detail = "orbit"
                self.screen = Orbit(self)
            case "Starport":
                self.location.detail = "starport"
                self.screen = Starport(self)
            case "Jump":
                self.location.detail = "jump"
                self.screen = Jump(self)
            case "Trade":
                self.location.detail = "trade"
                self.screen = Trade(self)
            case "Passengers":
                self.location.detail = "terminal"
                self.screen = Passengers(self)
            case _:
                raise ValueError(f"unrecognized menu item: '{new_state}'")

if __name__ == '__main__':
    Game().run()
