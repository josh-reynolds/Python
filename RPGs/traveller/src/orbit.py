"""Contains the OrbitScreen class.

OrbitScreen - contains commands for the orbit state.
"""
from typing import Any
from src.baggage import Baggage
from src.command import Command
from src.credits import Credits
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.passengers import Passage
from src.play import PlayScreen
from src.ship import RepairStatus
from src.utilities import die_roll

class OrbitScreen(PlayScreen):
    """Contains commands for the orbit state."""

    def __init__(self, parent: Any) -> None:
        """Create an OrbitScreen object."""
        super().__init__(parent)
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
        print(f"{BOLD_BLUE}Landing on {self.parent.location.name}.{END_FORMAT}")
        if not self.parent.ship.model.streamlined:
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
                self.parent.financials.credit(funds, "passenger fare")

                self._low_lottery(low_lottery_amount)

                self.parent.ship.passengers = []
                self.parent.ship.hold = [item for item in self.parent.ship.hold
                                  if not isinstance(item, Baggage)]

        self.parent.financials.berthing_fee(self.parent.location.on_surface())
        self.parent.change_state("Starport")
        return None

    def _low_lottery(self, low_lottery_amount) -> None:
        """Run the low passage lottery and apply results."""
        if self.parent.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.parent.ship.passengers if
                                         p.passage == Passage.LOW]
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
                self.parent.financials.credit(low_lottery_amount, "low lottery")

    def outbound_to_jump(self) -> None:
        """Move from orbit to the jump point."""
        print(f"{BOLD_BLUE}Travelling out to {self.parent.location.name} jump point.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot travel to the jump point.{END_FORMAT}")
            return None

        leg_fc = self._check_fuel_level("out to")
        if not leg_fc:
            return None

        self.parent.ship.current_fuel -= leg_fc
        self.parent.date.day += 1
        self.parent.change_state("Jump")
        return None

    # ACTIONS ==============================================================
