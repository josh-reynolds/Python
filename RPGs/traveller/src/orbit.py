"""Contains the OrbitScreen class.

OrbitScreen - contains commands for the orbit state.
"""
from typing import Any
from src.command import Command
from src.credits import Credits
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.model import Model, GuardClauseFailure
from src.play import PlayScreen

class OrbitScreen(PlayScreen):
    """Contains commands for the orbit state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create an OrbitScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('land', 'Land at starport', self.land),
                Command('outbound', 'Go to jump point', self.outbound_to_jump),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Orbit({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def land(self) -> None:
        """Move from orbit to the starport."""
        print(f"{BOLD_BLUE}Landing on {self.model.system_name()}.{END_FORMAT}")
        if not self.model.streamlined:
            print("Your ship is not streamlined and cannot land.")
            return None

        if not self.model.can_maneuver():
            print(f"{BOLD_RED}Drive failure. Cannot land.{END_FORMAT}")
            return None

        if self.model.destination() == self.model.get_star_system():
            if self.model.total_passenger_count > 0:
                print(f"Passengers disembarking on {self.model.system_name()}.")

                funds = Credits(sum(p.ticket_price.amount for p in \
                        self.model.get_passengers()))
                low_lottery_amount = Credits(10) * self.model.low_passenger_count
                funds -= low_lottery_amount
                print(f"Receiving {funds} in passenger fares.")
                self.model.credit(funds, "passenger fare")

                print(self.model.low_lottery(low_lottery_amount))

                self.model.set_passengers([])
                self.model.remove_baggage()

        self.model.set_location("starport")
        self.model.berthing_fee()
        self.parent.change_state("Starport")
        return None

    def outbound_to_jump(self) -> None:
        """Move from orbit to the jump point."""
        print(f"{BOLD_BLUE}Travelling out to {self.model.system_name()} jump point.{END_FORMAT}")
        try:
            print(self.model.outbound_to_jump())
            self.parent.change_state("Jump")
        except GuardClauseFailure as exception:
            print(exception)

    # ACTIONS ==============================================================
