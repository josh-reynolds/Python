"""Contains the OrbitScreen class.

OrbitScreen - contains commands for the orbit state.
"""
from typing import Any
from src.command import Command
from src.credits import Credits
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.model import Model
from src.play import PlayScreen
from src.utilities import die_roll

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

                self._low_lottery(low_lottery_amount)

                self.model.set_passengers([])
                self.model.remove_baggage()

        self.model.set_location("starport")
        self.model.berthing_fee()
        self.parent.change_state("Starport")
        return None

    def _low_lottery(self, low_lottery_amount) -> None:
        """Run the low passage lottery and apply results."""
        if self.model.low_passenger_count > 0:
            low_passengers = self.model.get_low_passengers()
            for passenger in low_passengers:
                if die_roll(2) + passenger.endurance + self.model.medic_skill() < 5:
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
                self.model.credit(low_lottery_amount, "low lottery")

    def outbound_to_jump(self) -> None:
        """Move from orbit to the jump point."""
        print(f"{BOLD_BLUE}Travelling out to {self.model.system_name()} jump point.{END_FORMAT}")
        result = self.model.outbound_to_jump()
        print(result[1])
        if result[0]:
            self.parent.change_state("Jump")

    # ACTIONS ==============================================================
