"""Contains the game loop and game logic for a Traveller trading simulation.

Game - contains the game loop and basic controller/view logic.
"""
from src.format import BOLD_YELLOW, BOLD_RED, END_FORMAT, BOLD_GREEN
from src.highport import HighportScreen
from src.jump import JumpScreen
from src.menu import MenuScreen
from src.model import Model
from src.orbit import OrbitScreen
from src.screen import Screen
from src.starport import StarportScreen
from src.terminal import TerminalScreen
from src.trade import TradeScreen
from src.utilities import int_input, confirm_input
from src.wilderness import WildernessScreen

class Game:
    """Contains the game loop and basic controller/view logic."""

    def __init__(self) -> None:
        """Create an instance of Game."""
        self.running = False
        self.screen: Screen = MenuScreen(self, Model(self))

    def __repr__(self) -> str:
        """Return the developer string representation of the Game object."""
        return "Game()"

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

    # TO_DO: incorporate other input flavors here: quit-int, choose_from, etc.
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
                self.screen = OrbitScreen(self, self.screen.model)
            case "Starport":
                self.screen = StarportScreen(self, self.screen.model)
            case "Highport":
                self.screen = HighportScreen(self, self.screen.model)
            case "Jump":
                self.screen = JumpScreen(self, self.screen.model)
            case "Trade":
                self.screen = TradeScreen(self, self.screen.model)
            case "Terminal":
                self.screen = TerminalScreen(self, self.screen.model)
            case "Wilderness":
                self.screen = WildernessScreen(self, self.screen.model)
            case _:
                raise ValueError(f"unrecognized menu item: '{new_state}'")

if __name__ == '__main__':
    Game().run()
