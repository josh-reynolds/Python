"""Contains the TradeScreen class.

TradeScreen - contains commands for the trade state.
"""
from typing import Any, cast, List, Tuple
from src.cargo import Cargo
from src.command import Command
from src.coordinate import Coordinate
from src.credits import Credits
from src.format import BOLD_BLUE, END_FORMAT, BOLD_RED
from src.model import Model
from src.freight import Freight
from src.play import PlayScreen
from src.star_system import Hex, StarSystem
from src.utilities import confirm_input, pr_list

class TradeScreen(PlayScreen):
    """Contains commands for the trade state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a TradeScreen object."""
        super().__init__(parent, model)
        self.commands += [
                Command('leave', 'Leave trade depot', self.leave_depot),
                Command('buy', 'Buy cargo', self.buy_cargo),
                Command('sell', 'Sell cargo', self.sell_cargo),
                Command('view goods', 'View trade goods', self.goods),
                Command('load freight', 'Load freight', self.load_freight),
                Command('unload freight', 'Unload freight', self.unload_freight),
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Trade({self.parent!r})"

    # VIEW COMMANDS ========================================================
    def goods(self) -> None:
        """Show goods available for purchase."""
        print(f"{BOLD_BLUE}Available cargo loads:{END_FORMAT}")
        pr_list(self.parent.model.depot.cargo)
        _ = input("\nPress ENTER key to continue.")

    # STATE TRANSITIONS ====================================================
    def leave_depot(self) -> None:
        """Move from the trade depot to the starport."""
        print(f"{BOLD_BLUE}Leaving {self.parent.model.location.name} trade depot.{END_FORMAT}")
        self.parent.change_state("Starport")

    # ACTIONS ==============================================================
    def buy_cargo(self) -> None:
        """Purchase cargo for speculative trade."""
        print(f"{BOLD_BLUE}Purchasing cargo.{END_FORMAT}")
        pr_list(self.parent.model.depot.cargo)
        cargo = self.parent.model.depot.get_cargo_lot(self.parent.model.depot.cargo, "buy")
        if cargo is None:
            return

        quantity = self.parent.model.depot.get_cargo_quantity("buy", cargo)
        if quantity is None:
            return

        if self.parent.model.depot.insufficient_hold_space(cargo,
                                                     quantity,
                                                     self.parent.model.ship.free_space()):
            return

        cost = self.parent.model.depot.determine_price("purchase", cargo, quantity,
                                          self.parent.model.ship.trade_skill())

        if self.parent.model.depot.insufficient_funds(cost, self.parent.model.financials.balance):
            return

        if not self.parent.model.depot.confirm_transaction("purchase", cargo, quantity, cost):
            return

        self.parent.model.depot.remove_cargo(self.parent.model.depot.cargo, cargo, quantity)

        purchased = Cargo(cargo.name, str(quantity), cargo.price, cargo.unit_size,
                          cargo.purchase_dms, cargo.sale_dms, self.parent.model.location)
        self.parent.model.ship.load_cargo(purchased)

        self.parent.model.financials.debit(cost, "cargo purchase")
        self.parent.model.date.day += 1

    def sell_cargo(self) -> None:
        """Sell cargo in speculative trade."""
        print(f"{BOLD_BLUE}Selling cargo.{END_FORMAT}")
        cargoes = [c for c in self.parent.model.ship.hold if isinstance(c, Cargo)]

        if len(cargoes) == 0:
            print("You have no cargo on board.")
            return

        pr_list(cargoes)
        cargo = self.parent.model.depot.get_cargo_lot(cargoes, "sell")
        if cargo is None:
            return

        if self.parent.model.depot.invalid_cargo_origin(cargo):
            return

        broker_skill = self.parent.model.depot.get_broker()

        quantity = self.parent.model.depot.get_cargo_quantity("sell", cargo)
        if quantity is None:
            return

        sale_price = self.parent.model.depot.determine_price("sale", cargo, quantity,
                                                broker_skill + self.parent.model.ship.trade_skill())

        self.parent.model.financials.debit(self.parent.model.depot.broker_fee(
                                            broker_skill, sale_price), "broker fee")

        if not self.parent.model.depot.confirm_transaction("sale", cargo, quantity, sale_price):
            return

        self.parent.model.depot.remove_cargo(self.parent.model.ship.hold, cargo, quantity)

        self.parent.model.financials.credit(sale_price, "cargo sale")
        self.parent.model.date.day += 1

    def load_freight(self) -> None:
        """Select and load Freight onto the Ship."""
        print(f"{BOLD_BLUE}Loading freight.{END_FORMAT}")

        jump_range = self.parent.model.ship.model.jump_range
        potential_destinations = self.parent.model.location.destinations.copy()
        destinations = self._get_destinations(potential_destinations,
                                              jump_range, "freight shipments")
        if not destinations:
            return

        coordinate, available = self.parent.model.depot.get_available_freight(destinations)
        if available is None:
            return

        destination = cast(StarSystem,
                           self.parent.model.star_map.get_system_at_coordinate(
                               cast(Coordinate, coordinate)))
        print(f"Freight shipments for {destination.name}")
        print(available)

        total_tonnage, selection = self._select_freight_lots(available, destination)

        if total_tonnage == 0:
            print("No freight shipments selected.")
            return
        print(f"{total_tonnage} tons selected.")

        confirmation = confirm_input(f"Load {total_tonnage} tons of freight? (y/n)? ")
        if confirmation == 'n':
            print("Cancelling freight selection.")
            return

        for entry in selection:
            self.parent.model.depot.freight[destination].remove(entry)
            self.parent.model.ship.load_cargo(Freight(entry,
                                         self.parent.model.location,
                                         destination))
        self.parent.model.date.day += 1

    def _select_freight_lots(self, available: List[int],
                             destination: Hex) -> Tuple[int, List[int]]:
        """Select Freight lots from a list of available shipments."""
        selection: List[int] = []
        total_tonnage = 0
        hold_tonnage = self.parent.model.ship.free_space()
        while True:
            if len(available) == 0:
                print(f"No more freight available for {destination.name}.")
                break

            # can't use int input here since we allow for 'q' as well...
            response: int | str = input("Choose a shipment by tonnage ('q' to exit): ")
            if response == 'q':
                break

            try:
                response = int(response)
            except ValueError:
                print("Please input a number.")
                continue

            if response in available:
                if response <= hold_tonnage:
                    # even though we cast to int above in try/catch,
                    # mypy is unaware, need to cast again to silence it.
                    # sort this out...
                    available.remove(cast(int, response))
                    selection.append(cast(int, response))
                    total_tonnage += response
                    hold_tonnage -= response
                    print(available)
                    print(f"Cargo space left: {hold_tonnage}")
                else:
                    print(f"{BOLD_RED}That shipment will not fit in your cargo hold.{END_FORMAT}")
                    print(f"{BOLD_RED}Hold free space: {hold_tonnage}{END_FORMAT}")
            else:
                print(f"{BOLD_RED}There are no shipments of size {response}.{END_FORMAT}")

        print("Done selecting shipments.")
        return (total_tonnage, selection)

    def unload_freight(self) -> None:
        """Unload Freight from the Ship and receive payment."""
        print(f"{BOLD_BLUE}Unloading freight.{END_FORMAT}")

        # truth table: passengers, freight, destination flag,...

        # It should not be possible for there to be freight in the hold,
        # and a destination flag set to None. Should we assert just
        # in case, so we could track down any such bug:
        if self.parent.model.ship.destination is None:
            print("You have no contracted destination.")
            return

        freight = [f for f in self.parent.model.ship.hold if isinstance(f, Freight)]
        if len(freight) == 0:
            print("You have no freight on board.")
            return

        if self.parent.model.ship.destination == self.parent.model.location:
            freight_tonnage = sum(f.tonnage for f in freight)
            self.parent.model.ship.hold = [c for c in self.parent.model.ship.hold
                                           if isinstance(c, Cargo)]

            payment = Credits(1000 * freight_tonnage)
            self.parent.model.financials.credit(Credits(1000 * freight_tonnage), "freight shipment")
            print(f"Receiving payment of {payment} for {freight_tonnage} tons shipped.")

            self.parent.model.date.day += 1

        else:
            print(f"{BOLD_RED}You are not at the contracted "
                  f"destination for this freight.{END_FORMAT}")
            print(f"{BOLD_RED}It should be unloaded at "
                  f"{self.parent.model.ship.destination.name}.{END_FORMAT}")
