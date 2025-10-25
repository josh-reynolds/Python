"""Contains the game loop and game logic for a Traveller trading simulation.

Game - contains the game loop and all game logic.
"""
from typing import List, Tuple, cast
from calendar import Calendar
from random import randint, choice
from financials import Financials, Credits
from command import Command
from coordinate import Coordinate
from menu import Menu
from utilities import int_input, confirm_input
from utilities import pr_list, die_roll
from utilities import BOLD_YELLOW, BOLD_BLUE
from utilities import BOLD_RED, END_FORMAT, BOLD_GREEN
from ship import Ship, FuelQuality, RepairStatus
from cargo import Cargo, CargoDepot, Freight
from star_system import DeepSpace, Hex, StarSystem
from star_map import StarMap, StarSystemFactory

# pylint: disable=R0902, R0904
# R0902: Too many instance attributes (8/7)
# R0904: Too many public methods (34/20)
class Game:
    """Contains the game loop and all game logic."""

    def __init__(self) -> None:
        """Create an instance of Game."""
        self.running = False
        self.screen = Menu(self)
        self.date = Calendar()

        self.ship = Ship()
        self.ship.load_cargo(Cargo("Grain", '20', Credits(300), 1,
                                   {"Ag":-2,"Na":1,"In":2},
                                   {"Ag":-2}))

        self.star_map = StarMap({
            (0,0,0)  : StarSystemFactory.create("Yorbund", (0,0,0), "A", 8, 7, 5, 9, 5, 5, 10),
            (0,1,-1) : DeepSpace((0,1,-1)),
            (0,-1,1) : StarSystemFactory.create("Mithril", (0,-1,1), "A", 8, 4, 0, 7, 5, 5, 10),
            (1,0,-1) : StarSystemFactory.create("Kinorb", (1,0,-1), "A", 8, 5, 5, 7, 5, 5, 10),
            (-1,0,1) : DeepSpace((-1,0,1)),
            (1,-1,0) : DeepSpace((1,-1,0)),
            (-1,1,0) : StarSystemFactory.create("Aramis", (-1,1,0), "A", 8, 6, 5, 8, 5, 5, 10)
            })

        self.location = cast(StarSystem, self.star_map.get_system_at_coordinate((0,0,0)))
        coord = self.location.coordinate
        self.location.destinations = self.star_map.get_systems_within_range(coord,
                                                              self.ship.jump_range)
        self.financials = Financials(10000000, self.date.current_date, self.ship, self.location)
        self.depot = CargoDepot(self.location, self.date.current_date)
        self.commands: List[Command] = []

        self.ship.add_observer(self)
        self.ship.controls = self
        self.depot.add_observer(self)
        self.depot.controls = self
        self.financials.add_observer(self)

        self.date.add_observer(self.depot)
        self.date.add_observer(self.financials)

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
        self.commands = Commands.jump   # awkward, needs to change
                                            # when location ctor detail changes
        while self.running:
            self.screen = self.screen.update()

    # ACTIONS ==============================================================
    def _misjump_check(self, destination: Coordinate) -> None:
        """Test for misjump and report results."""
        if self.ship.fuel_quality == FuelQuality.UNREFINED:
            modifier = 3
        else:
            modifier = -1
        if self.financials.maintenance_status(self.date.current_date) == "red":
            modifier += 2

        misjump_check = die_roll(2) + modifier
        if misjump_check > 11:
            print(f"{BOLD_RED}MISJUMP!{END_FORMAT}")
            # TO_DO: all this should move to live with the other
            #        three-axis calculations
            distance = randint(1,36)
            hexes = [(0,distance,-distance),
                     (0,-distance,distance),
                     (distance,0,-distance),
                     (-distance,0,distance),
                     (distance,-distance,0),
                     (-distance,distance,0)]
            misjump_target = choice(hexes)
            misjump_target = (misjump_target[0] + self.location.coordinate[0],
                           misjump_target[1] + self.location.coordinate[1],
                           misjump_target[2] + self.location.coordinate[2])
            print(f"{misjump_target} at distance {distance}")

            # misjump is the only scenario where EmptySpace is a possible
            # location, so we need to leave this type as Hex
            self.location = self.star_map.get_system_at_coordinate(misjump_target) # type: ignore
            self.star_map.systems[misjump_target] = self.location
        else:
            self.location = cast(StarSystem, self.star_map.get_system_at_coordinate(destination))

    def jump(self) -> None:
        """Perform a hyperspace jump to another StarSystem."""
        print(f"{BOLD_BLUE}Preparing for jump.{END_FORMAT}")

        status = self.financials.maintenance_status(self.date.current_date)
        self.ship.check_failure_pre_jump(status)
        if self.ship.repair_status in (RepairStatus.BROKEN, RepairStatus.PATCHED):
            print(f"{BOLD_RED}Drive failure. Cannot perform jump.{END_FORMAT}")
            return

        if not self.ship.sufficient_jump_fuel():
            print(self.ship.insufficient_jump_fuel_message())
            return

        if not self.ship.sufficient_life_support():
            print(self.ship.insufficient_life_support_message())
            return

        jump_range = self.ship.jump_range
        print(f"Systems within jump-{jump_range}:")
        pr_list(self.location.destinations)
        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(self.location.destinations):
            print("That is not a valid destination number.")
            return

        coordinate = self.location.destinations[destination_number].coordinate
        destination = cast(StarSystem, self.star_map.get_system_at_coordinate(coordinate))

        self.ship.warn_if_not_contracted(destination)

        confirmation = confirm_input(f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling jump.")
            return

        if self.ship.fuel_quality == FuelQuality.UNREFINED:
            self.ship.unrefined_jump_counter += 1

        print(f"{BOLD_RED}Executing jump!{END_FORMAT}")

        self._misjump_check(coordinate)
        self.location.detail = "jump"
        self.commands = Commands.jump

        self.ship.check_failure_post_jump()

        coord = self.location.coordinate
        self.location.destinations = self.star_map.get_systems_within_range(coord,
                                                   jump_range)

        self.depot = CargoDepot(self.location, self.date.current_date)
        self.depot.add_observer(self)
        self.depot.controls = self
        self.financials.location = destination

        self.ship.life_support_level = 0
        self.ship.current_fuel -= self.ship.jump_fuel_cost
        self.date.plus_week()

    def buy_cargo(self) -> None:
        """Purchase cargo for speculative trade."""
        print(f"{BOLD_BLUE}Purchasing cargo.{END_FORMAT}")
        pr_list(self.depot.cargo)
        cargo = self.depot.get_cargo_lot(self.depot.cargo, "buy")
        if cargo is None:
            return

        quantity = self.depot.get_cargo_quantity("buy", cargo)
        if quantity is None:
            return

        if self.depot.insufficient_hold_space(cargo, quantity, self.ship.free_space()):
            return

        cost = self.depot.determine_price("purchase", cargo, quantity,
                                          self.ship.trade_skill())

        if self.depot.insufficient_funds(cost, self.financials.balance):
            return

        if not self.depot.confirm_transaction("purchase", cargo, quantity, cost):
            return

        self.depot.remove_cargo(self.depot.cargo, cargo, quantity)

        purchased = Cargo(cargo.name, str(quantity), cargo.price, cargo.unit_size,
                          cargo.purchase_dms, cargo.sale_dms, self.location)
        self.ship.load_cargo(purchased)

        self.financials.debit(cost)
        self.date.day += 1

    def sell_cargo(self) -> None:
        """Sell cargo in speculative trade."""
        print(f"{BOLD_BLUE}Selling cargo.{END_FORMAT}")
        cargoes = [c for c in self.ship.hold if isinstance(c, Cargo)]

        if len(cargoes) == 0:
            print("You have no cargo on board.")
            return

        pr_list(cargoes)
        cargo = self.depot.get_cargo_lot(cargoes, "sell")
        if cargo is None:
            return

        if self.depot.invalid_cargo_origin(cargo):
            return

        broker_skill = self.depot.get_broker()

        quantity = self.depot.get_cargo_quantity("sell", cargo)
        if quantity is None:
            return

        sale_price = self.depot.determine_price("sale", cargo, quantity,
                                                broker_skill + self.ship.trade_skill())

        self.financials.debit(self.depot.broker_fee(broker_skill, sale_price))

        if not self.depot.confirm_transaction("sale", cargo, quantity, sale_price):
            return

        self.depot.remove_cargo(self.ship.hold, cargo, quantity)

        self.financials.credit(sale_price)
        self.date.day += 1

    # Book 2 p. 35
    # Unrefined fuel may be obtained by skimming the atmosphere of a
    # gas giant if unavailable elsewhere. Most star systems have at
    # least one...
    #
    # Traveller '77 does not restrict this to streamlined ships, and
    # also does not include ocean refuelling, but I think I will be
    # including both options. (In all likelihood this will lean heavily
    # toward second edition...)
    def skim(self) -> None:
        """Refuel the Ship by skimming from a gas giant planet."""
        print(f"{BOLD_BLUE}Skimming fuel from a gas giant planet.{END_FORMAT}")
        if not self.location.gas_giant:
            # TO_DO: may want to tweak this message in deep space.
            print("There is no gas giant in this system. No fuel skimming possible.")
            return

        if not self.ship.streamlined:
            print("Your ship is not streamlined and cannot skim fuel.")
            return

        if self.ship.repair_status == RepairStatus.BROKEN:
            print(f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")
            return

        if self.ship.current_fuel == self.ship.fuel_tank:
            print("Fuel tank is already full.")
            return

        self.ship.current_fuel = self.ship.fuel_tank
        self.ship.fuel_quality = FuelQuality.UNREFINED
        self.date.day += 1

    def _get_freight_destinations(self, potential_destinations: List[StarSystem],
                                  jump_range: int) -> List[StarSystem]:
        """Return a list of all reachable destinations with Freight lots."""
        result: List[StarSystem] = []
        if self.ship.destination is not None:
            if self.ship.destination == self.location:
                print(f"{BOLD_RED}There is still freight to be unloaded "
                      f"on {self.location.name}.{END_FORMAT}")
                return result
            if self.ship.destination in potential_destinations:
                print("You are under contract. Only showing freight " +
                      f"for {self.ship.destination.name}:\n")
                result = [self.ship.destination]
            else:
                print(f"You are under contract to {self.ship.destination.name} " +
                      "but it is not within jump range of here.")

        else:
            print(f"Available freight shipments within jump-{jump_range}:\n")
            result = potential_destinations

        return result

    def _select_freight_lots(self, available: List[int],
                             destination: Hex) -> Tuple[int, List[int]]:
        """Select Freight lots from a list of available shipments."""
        selection: List[int] = []
        total_tonnage = 0
        hold_tonnage = self.ship.free_space()
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

    def load_freight(self) -> None:
        """Select and load Freight onto the Ship."""
        print(f"{BOLD_BLUE}Loading freight.{END_FORMAT}")

        jump_range = self.ship.jump_range
        potential_destinations = self.location.destinations.copy()
        destinations = self._get_freight_destinations(potential_destinations, jump_range)
        if not destinations:
            return

        coordinate, available = self.depot.get_available_freight(destinations)
        if available is None:
            return

        destination = cast(StarSystem,
                           self.star_map.get_system_at_coordinate(
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
            self.depot.freight[destination].remove(entry)
            self.ship.load_cargo(Freight(entry,
                                         self.location,
                                         destination))
        self.date.day += 1

    def unload_freight(self) -> None:
        """Unload Freight from the Ship and receive payment."""
        print(f"{BOLD_BLUE}Unloading freight.{END_FORMAT}")

        # truth table: passengers, freight, destination flag,...

        # It should not be possible for there to be freight in the hold,
        # and a destination flag set to None. Should we assert just
        # in case, so we could track down any such bug:
        if self.ship.destination is None:
            print("You have no contracted destination.")
            return

        freight = [f for f in self.ship.hold if isinstance(f, Freight)]
        if len(freight) == 0:
            print("You have no freight on board.")
            return

        if self.ship.destination == self.location:
            freight_tonnage = sum(f.tonnage for f in freight)
            self.ship.hold = [c for c in self.ship.hold if isinstance(c, Cargo)]

            payment = Credits(1000 * freight_tonnage)
            self.financials.credit(Credits(1000 * freight_tonnage))
            print(f"Receiving payment of {payment} for {freight_tonnage} tons shipped.")

            self.date.day += 1

        else:
            print(f"{BOLD_RED}You are not at the contracted "
                  f"destination for this freight.{END_FORMAT}")
            print(f"{BOLD_RED}It should be unloaded at "
                  f"{self.ship.destination.name}.{END_FORMAT}")

game = Game()

# pylint: disable=R0903
# R0903: Too few public methods (0/2)
class Commands:
    """Collects all command sets together."""

    jump = [
            Command('j', 'Jump to new system', game.jump),
            Command('s', 'Skim fuel from gas giant', game.skim),
            ]
    jump = sorted(jump, key=lambda command: command.key)

    trade = [
            Command('b', 'Buy cargo', game.buy_cargo),
            Command('s', 'Sell cargo', game.sell_cargo),
            Command('f', 'Load freight', game.load_freight),
            Command('u', 'Unload freight', game.unload_freight)
            ]
    trade = sorted(trade, key=lambda command: command.key)

# keeping command characters straight...
# ALWAYS:   ? a ~ c d e ~ ~ h ~ ~ k ~ ~ ~ ~ q ~ ~ ~ ~ v w
# STARPORT:             f           l m n p   r   t u
# ORBIT:                  g         l
# JUMP:                       i j               s
# TRADE:        b       f g         l           s   u
# PASSENGERS:   b                   l

if __name__ == '__main__':
    game.run()
