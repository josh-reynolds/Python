"""Contains the StarportScreen class.

StarportScreen - contains commands for the starport state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.model import Model
from src.passengers import Passage
from src.play import PlayScreen
from src.ship import RepairStatus, FuelQuality
from src.utilities import confirm_input

class StarportScreen(PlayScreen):
    """Contains commands for the starport state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a StarportScreen object."""
        super().__init__(parent, model)
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

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Starport({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def liftoff(self) -> None:
        """Move from the starport to orbit."""
        print(f"{BOLD_BLUE}Lifting off to orbit {self.model.location.name}.{END_FORMAT}")

        if not self.model.can_travel():
            print(f"{BOLD_RED}Drive failure. Cannot lift off.{END_FORMAT}")
            return None

        # corner case - these messages assume passengers are coming
        # from the current world, which should be true most
        # of the time, but not necessarily all the time
        if self.model.ship.total_passenger_count > 0:
            print(f"Boarding {self.model.ship.total_passenger_count} "   # type: ignore[union-attr]
                  f"passengers for {self.model.ship.destination.name}.")

        if self.model.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.model.ship.passengers if
                              p.passage == Passage.LOW]
            for passenger in low_passengers:
                passenger.guess_survivors(self.model.ship.low_passenger_count)

        self.model.location.detail = "orbit"
        self.parent.change_state("Orbit")
        return None

    def to_depot(self) -> None:
        """Move from the starport to the trade depot."""
        print(f"{BOLD_BLUE}Entering {self.model.location.name} trade depot.{END_FORMAT}")
        self.model.location.detail = "trade"
        self.parent.change_state("Trade")

    def to_terminal(self) -> None:
        """Move from the starport to the passenger terminal."""
        print(f"{BOLD_BLUE}Entering {self.model.location.name} " +
              f"passenger terminal.{END_FORMAT}")
        self.model.location.detail = "terminal"
        self.parent.change_state("Terminal")

    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        cost = self.model.ship.recharge()
        self.model.financials.debit(cost, "life support")

    def refuel(self) -> None:
        """Refuel the Ship."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        if self.model.location.starport in ('E', 'X'):
            print(f"No fuel is available at starport {self.model.location.starport}.")
            return

        cost = self.model.ship.refuel(self.model.location.starport)
        self.model.financials.debit(cost, "refuelling")

    def maintenance(self) -> None:
        """Perform annual maintenance on the Ship."""
        print(f"{BOLD_BLUE}Performing annual ship maintenance.{END_FORMAT}")
        if self.model.location.starport not in ('A', 'B'):
            print("Annual maintenance can only be performed at class A or B starports.")
            return

        cost = self.model.ship.maintenance_cost()
        if self.model.financials.balance < cost:
            print("You do not have enough funds to pay for maintenance.\n"
                  f"It will cost {cost}. Your balance is {self.model.financials.balance}.")
            return

        if self.model.financials.maintenance_status(self.model.date.current_date) == \
                "green":
            confirmation = confirm_input("Maintenance was performed less than 10 months " +
                                         "ago. Continue (y/n)? ")
            if confirmation == "n":
                return

        confirmation = confirm_input(f"Maintenance will cost {cost} and take " +
                                     "two weeks. Continue (y/n)? ")
        if confirmation == "n":
            return

        print(f"Performing maintenance. Charging {cost}.")
        self.model.financials.last_maintenance = self.model.date.current_date
        self.model.financials.debit(cost, "annual maintenance")
        self.model.date.day += 14    # should we wrap this in a method call?
        self.model.ship.repair_status = RepairStatus.REPAIRED

    def flush(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        print(f"{BOLD_BLUE}Flushing out fuel tanks.{END_FORMAT}")
        if self.model.ship.fuel_quality == FuelQuality.REFINED:
            print("Ship fuel tanks are clean. No need to flush.")
            return

        if self.model.location.starport in ('E', 'X'):
            print(f"There are no facilities to flush tanks "
                  f"at starport {self.model.location.starport}.")
            return

        print("Fuel tanks have been decontaminated.")
        self.model.ship.fuel_quality = FuelQuality.REFINED
        self.model.ship.unrefined_jump_counter = 0
        self.model.date.plus_week()

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self) -> None:
        """Fully repair damage to the Ship (Starport)."""
        print(f"{BOLD_BLUE}Starport repairs.{END_FORMAT}")
        print(self.model.repair_ship())
