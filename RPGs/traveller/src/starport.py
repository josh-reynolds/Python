"""Contains the Starport screen class.

Starport - contains commands for the Starport state.
"""
from typing import Any, cast
from src.command import Command
from src.menu import Trade
from src.orbit import Orbit
from src.passengers import PassageClass
from src.play import Play
from src.screen import ScreenT
from src.terminal import Passengers
from src.ship import RepairStatus, FuelQuality
from src.utilities import BOLD_BLUE, END_FORMAT, BOLD_RED

class Starport(Play):
    """Contains commands for the Starport state."""

    def __init__(self, parent: Any) -> None:
        """Create a Starport object."""
        super().__init__(parent)
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

    def __str__(self) -> str:
        """Return the string representation of the current screen."""
        return "Starport"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    def liftoff(self: ScreenT) -> None | ScreenT:
        """Move from the starport to orbit."""
        print(f"{BOLD_BLUE}Lifting off to orbit {self.parent.location.name}.{END_FORMAT}")

        if self.parent.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot lift off.{END_FORMAT}")
            return None

        # corner case - these messages assume passengers are coming
        # from the current world, which should be true most
        # of the time, but not necessarily all the time
        if self.parent.ship.total_passenger_count > 0:
            print(f"Boarding {self.parent.ship.total_passenger_count} passengers "
                  f"for {self.parent.ship.destination.name}.")

        if self.parent.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.parent.ship.passengers if
                              p.passage == PassageClass.LOW]
            for passenger in low_passengers:
                passenger.guess_survivors(self.parent.ship.low_passenger_count)

        self.parent.location.detail = "orbit"
        return cast(ScreenT, Orbit(self.parent))

    def to_depot(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the trade depot."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} trade depot.{END_FORMAT}")
        self.parent.location.detail = "trade"
        return cast(ScreenT, Trade(self.parent))

    def to_terminal(self: ScreenT) -> None | ScreenT:
        """Move from the starport to the passenger terminal."""
        print(f"{BOLD_BLUE}Entering {self.parent.location.name} passenger terminal.{END_FORMAT}")
        self.parent.location.detail = "terminal"
        return cast(ScreenT, Passengers(self.parent))

    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        cost = self.parent.ship.recharge()
        self.parent.financials.debit(cost, "life support")

    def refuel(self) -> None:
        """Refuel the Ship."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        if self.parent.location.starport in ('E', 'X'):
            print(f"No fuel is available at starport {self.parent.location.starport}.")
            return

        cost = self.parent.ship.refuel(self.parent.location.starport)
        self.parent.financials.debit(cost, "refuelling")

    def maintenance(self) -> None:
        """Perform annual maintenance on the Ship."""
        print(f"{BOLD_BLUE}Performing annual ship maintenance.{END_FORMAT}")
        if self.parent.location.starport not in ('A', 'B'):
            print("Annual maintenance can only be performed at class A or B starports.")
            return

        cost = self.parent.ship.maintenance_cost()
        if self.parent.financials.balance < cost:
            print("You do not have enough funds to pay for maintenance.\n"
                  f"It will cost {cost}. Your balance is {self.parent.financials.balance}.")
            return

        # TO_DO: should we have a confirmation here?
        # TO_DO: should we warn or block if maintenance was performed recently?
        print(f"Performing maintenance. This will take two weeks. Charging {cost}.")
        self.parent.financials.last_maintenance = self.parent.date.current_date
        self.parent.financials.debit(cost, "annual maintenance")
        self.parent.date.day += 14    # should we wrap this in a method call?
        self.parent.ship.repair_status = RepairStatus.REPAIRED

    def flush(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        print(f"{BOLD_BLUE}Flushing out fuel tanks.{END_FORMAT}")
        if self.parent.ship.fuel_quality == FuelQuality.REFINED:
            print("Ship fuel tanks are clean. No need to flush.")
            return
        if self.parent.location.starport in ('E', 'X'):
            print(f"There are no facilities to flush tanks "
                  f"at starport {self.parent.location.starport}.")
            return

        print("Fuel tanks have been decontaminated.")
        self.parent.ship.fuel_quality = FuelQuality.REFINED
        self.parent.ship.unrefined_jump_counter = 0
        self.parent.date.plus_week()

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self) -> None:
        """Fully repair damage to the Ship (Starport)."""
        print(f"{BOLD_BLUE}Starport repairs.{END_FORMAT}")
        if self.parent.location.starport in ["D", "E", "X"]:
            print(f"No repair facilities available at starport {self.parent.location.starport}")
            return
        if self.parent.ship.repair_status == RepairStatus.REPAIRED:
            print("Your ship is not damaged.")
            return

        print("Your ship is fully repaired and decontaminated.")
        self.parent.ship.repair_status = RepairStatus.REPAIRED
        self.parent.ship.fuel_quality = FuelQuality.REFINED
        self.parent.ship.unrefined_jump_counter = 0
        self.parent.date.plus_week()
