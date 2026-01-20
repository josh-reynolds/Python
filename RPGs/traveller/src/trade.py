"""Contains the TradeScreen class.

TradeScreen - contains commands for the trade state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen
from src.utilities import pr_list

class TradeScreen(PlayScreen):
    """Contains commands for the trade state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a TradeScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('leave', 'Leave trade depot', self.to_downport),
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

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Trade({self.parent!r})"

    # VIEW COMMANDS ========================================================
    def goods(self) -> None:
        """Show goods available for purchase."""
        print(f"{BOLD_BLUE}Available cargo loads:{END_FORMAT}")
        pr_list(self.model.cargo)
        _ = input("\nPress ENTER key to continue.")

    # STATE TRANSITIONS ====================================================
    def to_downport(self) -> None:
        """Move from the trade depot to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.model.system_name()} trade depot.{END_FORMAT}")
        print(self.model.to_starport())
        self.parent.change_state("Downport")

    # ACTIONS ==============================================================
    def buy_cargo(self) -> None:
        """Purchase cargo for speculative trade."""
        print(f"{BOLD_BLUE}Purchasing cargo.{END_FORMAT}")
        try:
            print(self.model.buy_cargo())
        except GuardClauseFailure as exception:
            print(exception)

    def sell_cargo(self) -> None:
        """Sell cargo in speculative trade."""
        print(f"{BOLD_BLUE}Selling cargo.{END_FORMAT}")
        try:
            print(self.model.sell_cargo())
        except GuardClauseFailure as exception:
            print(exception)

    def load_freight(self) -> None:
        """Select and load Freight onto the Ship."""
        print(f"{BOLD_BLUE}Loading freight.{END_FORMAT}")
        try:
            print(self.model.load_freight())
        except GuardClauseFailure as exception:
            print(exception)

    def unload_freight(self) -> None:
        """Unload Freight from the Ship and receive payment."""
        print(f"{BOLD_BLUE}Unloading freight.{END_FORMAT}")
        try:
            print(self.model.unload_freight())
        except GuardClauseFailure as exception:
            print(exception)
