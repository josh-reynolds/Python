"""Contains the StarportScreen class.

StarportScreen - contains commands for the starport state.
"""
from typing import Any
from src.command import Command
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.model import Model
from src.play import PlayScreen
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
        print(f"{BOLD_BLUE}Lifting off to orbit {self.model.system_name()}.{END_FORMAT}")

        if not self.model.can_maneuver():
            print(f"{BOLD_RED}Drive failure. Cannot lift off.{END_FORMAT}")
            return None

        # corner case - these messages assume passengers are coming
        # from the current world, which should be true most
        # of the time, but not necessarily all the time
        if self.model.total_passenger_count > 0:
            print(f"Boarding {self.model.total_passenger_count} "
                  f"passengers for {self.model.destination_name}.")

        if self.model.low_passenger_count > 0:
            low_passengers = self.model.get_low_passengers()
            for passenger in low_passengers:
                passenger.guess_survivors(self.model.low_passenger_count)

        self.model.set_location("orbit")
        self.parent.change_state("Orbit")
        return None

    def to_depot(self) -> None:
        """Move from the starport to the trade depot."""
        print(f"{BOLD_BLUE}Entering {self.model.system_name()} trade depot.{END_FORMAT}")
        self.model.set_location("trade")
        self.parent.change_state("Trade")

    def to_terminal(self) -> None:
        """Move from the starport to the passenger terminal."""
        print(f"{BOLD_BLUE}Entering {self.model.system_name()} " +
              f"passenger terminal.{END_FORMAT}")
        self.model.set_location("terminal")
        self.parent.change_state("Terminal")

    # ACTIONS ==============================================================
    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self) -> None:
        """Recharge the Ship's life support system."""
        print(f"{BOLD_BLUE}Replenishing life support system.{END_FORMAT}")
        self.model.recharge_life_support()

    def refuel(self) -> None:
        """Refuel the Ship."""
        print(f"{BOLD_BLUE}Refuelling ship.{END_FORMAT}")
        print(self.model.refuel())

    def maintenance(self) -> None:
        """Perform annual maintenance on the Ship."""
        print(f"{BOLD_BLUE}Performing annual ship maintenance.{END_FORMAT}")
        if self.model.no_shipyard():
            print("Annual maintenance can only be performed at class A or B starports.")
            return

        cost = self.model.maintenance_cost()
        if self.model.balance < cost:
            print("You do not have enough funds to pay for maintenance.\n"
                  f"It will cost {cost}. Your balance is {self.model.balance}.")
            return

        if self.model.maintenance_status(self.model.get_current_date()) == \
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
        self.model.financials.last_maintenance = self.model.get_current_date()
        self.model.debit(cost, "annual maintenance")
        self.model.plus_week()
        print(self.model.repair_ship())

    def flush(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        print(f"{BOLD_BLUE}Flushing out fuel tanks.{END_FORMAT}")
        if not self.model.tanks_are_polluted():
            print("Ship fuel tanks are clean. No need to flush.")
            return

        if not self.model.can_flush():
            print(f"There are no facilities to flush tanks "
                  f"at starport {self.model.starport}.")
            return

        print("Fuel tanks have been decontaminated.")
        self.model.clean_fuel_tanks()
        self.model.plus_week()

    def repair_ship(self) -> None:
        """Fully repair damage to the Ship (Starport)."""
        print(f"{BOLD_BLUE}Starport repairs.{END_FORMAT}")
        print(self.model.repair_ship())
