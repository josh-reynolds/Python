"""Contains the game simulation model with references to all component objects.

Model - contains references to all game model objects.

Error - base class for exceptions thrown from this module.

GuardClauseFailure - thrown when a guard clause in the method did not pass.
"""
from typing import List, Any, cast, Dict, Tuple
from src.baggage import Baggage
from src.calendar import Calendar, modify_calendar_from
from src.cargo import Cargo
from src.cargo_depot import CargoDepot
from src.coordinate import Coordinate, get_misjump_target
from src.credits import Credits
from src.crew import Crew
from src.financials import Financials, financials_from
from src.format import BOLD_RED, BOLD_GREEN, END_FORMAT
from src.freight import Freight
from src.passengers import Passenger, Passage
from src.ship import Ship, RepairStatus, FuelQuality, ship_from
from src.star_system import StarSystem, Hex, DeepSpace
from src.star_map import StarMap
from src.subsector import Subsector
from src.utilities import die_roll, get_plural_suffix

# pylint: disable=R0904, R0902, C0302
# R0904: too many public methods (21/20)
# R0902: too many instance attributes (8/7)
# C0302: too many lines in module (1034/1000)
class Model:
    """Contains references to all game model objects."""

    # TO_DO: we don't have type for Controls or Observers
    def __init__(self, controls: Any) -> None:
        """Create an instance of a Model object."""
        self.date: Calendar
        self.ship: Ship
        self.star_map: StarMap
        self.map_hex: Hex
        self.financials: Financials
        self.depot: CargoDepot

        self.views: List[Any] = [controls]
        self.controls = controls

    def __repr__(self) -> str:
        """Return the developer string representation of the Model object."""
        return "Model()"

    def get_input(self, constraint: str, prompt: str) -> str | int:
        """Request input from controls."""
        return self.controls.get_input(constraint, prompt)    # type: ignore[union-attr]

    # TO_DO: is this ever called?
    def add_view(self, view: Any) -> None:
        """Add an view to respond to UI messages."""
        self.views.append(view)

    def message_views(self, message: str, priority: str="") -> None:
        """Pass a message on to all views."""
        for view in self.views:
            view.on_notify(message, priority)

    # TRANSITIONS =======================================
    def inbound_from_jump(self) -> str:
        """Move from the jump point to orbit."""
        if self._in_deep_space():
            raise GuardClauseFailure(f"{BOLD_RED}You are in deep space. " +\
                           f"There is no inner system to travel to.{END_FORMAT}")

        if not self._can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot travel " +\
                                     f"to orbit.{END_FORMAT}")

        leg_fc = self._check_fuel_level()
        if not leg_fc:
            raise GuardClauseFailure("Insufficient fuel to travel in from the jump point.")

        self._burn_fuel(leg_fc)
        self._add_day()
        self.set_location("orbit")
        return "Successfully travelled in to orbit."

    def outbound_to_jump(self) -> str:
        """Move from orbit to the jump point."""
        if not self._can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot " +\
                                     f"travel to the jump point.{END_FORMAT}")

        leg_fc = self._check_fuel_level()
        if not leg_fc:
            raise GuardClauseFailure("Insufficient fuel to travel out to the jump point.")

        self._burn_fuel(leg_fc)
        self._add_day()
        self.set_location("jump")
        return "Successfully travelled out to the jump point."

    # TO_DO: should merge with wilderness()
    def land(self) -> str:
        """Move from orbit to the starport."""
        if not self.ship.model.streamlined:
            raise GuardClauseFailure("Your ship is not streamlined and cannot land.")

        if not self._can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot land.{END_FORMAT}")

        result = ""
        if self.ship.destination == self.get_star_system():
            if self.ship.total_passenger_count > 0:
                result += f"Passengers disembarking on {self.system_name()}.\n"

                funds = Credits(sum(p.ticket_price.amount for p in \
                        self.get_passengers()))
                low_lottery_amount = Credits(10) * self.low_passenger_count
                funds -= low_lottery_amount
                result += f"Receiving {funds} in passenger fares.\n"
                self.financials.credit(funds, "passenger fare")

                result += self._low_lottery(low_lottery_amount)

                self.set_passengers([])
                self._remove_baggage()

        self.set_location("starport")
        self.financials.berthing_fee(self._at_starport)
        result += f"\nLanded at the {self.system_name()} starport."""
        return result

    def wilderness(self) -> str:
        """Move from orbit to the planet's surface."""
        if not self.ship.model.streamlined:
            raise GuardClauseFailure("Your ship is not streamlined and cannot land.")

        if not self._can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot land.{END_FORMAT}")

        self.set_location("wilderness")
        return f"\nLanded on the surface of {self.system_name()}."""

    def to_depot(self) -> str:
        """Move from the starport to the trade depot."""
        self.set_location("trade")
        return f"Entered the {self.system_name()} cargo depot."

    def to_terminal(self) -> str:
        """Move from the starport to the passenger terminal."""
        self.set_location("terminal")
        return f"Entered the {self.system_name()} passenger terminal."

    def to_starport(self) -> str:
        """Move to the starport from the depot or terminal."""
        self.set_location("starport")
        return f"Entered the {self.system_name()} starport."

    def liftoff(self) -> str:
        """Move from the starport to orbit."""
        try:
            result = self.to_orbit()
        except GuardClauseFailure as exception:
            raise GuardClauseFailure(f'{exception}') from exception

        passenger_string = ""
        # corner case - these messages assume passengers are coming
        # from the current world, which should be true most
        # of the time, but not necessarily all the time
        if self.ship.total_passenger_count > 0:
            passenger_string += f"Boarding {self.ship.total_passenger_count} "
            passenger_string += f"passengers for {self._destination_name}.\n"

        if self.low_passenger_count > 0:
            low_passengers = self._get_low_passengers()
            for passenger in low_passengers:
                passenger.guess_survivors(self.low_passenger_count)

        result = passenger_string + result
        return result

    def to_orbit(self) -> str:
        """Move from the planet surface to orbit."""
        if not self._can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot lift off.{END_FORMAT}")

        self.set_location("orbit")
        return f"Successfully lifted off to orbit from {self.system_name()}."

    # PROCEDURES ========================================
    def damage_control(self) -> str:
        """Repair damage to the Ship (Engineer)."""
        if self.ship.repair_status == RepairStatus.REPAIRED:
            return "Your ship is not damaged."

        if self.ship.repair_status == RepairStatus.PATCHED:
            return "Further repairs require starport facilities."

        self._add_day()
        if die_roll(2) + self.ship.engineering_skill() > 9:
            self.ship.repair_status = RepairStatus.PATCHED
            return "Ship partially repaired. Visit a starport for further work."
        return "No progress today. Drives are still out of commission."

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self) -> str:
        """Fully repair damage to the Ship (Starport)."""
        if self._starport in ["D", "E", "X"]:
            return f"No repair facilities available at starport {self._starport}"

        if self.ship.repair_status == RepairStatus.REPAIRED:
            return "Your ship is not damaged."

        self.ship.repair_status = RepairStatus.REPAIRED
        self._clean_fuel_tanks()
        self.plus_week()
        return "Your ship is fully repaired and decontaminated."

    # Book 2 pp. 5-6
    # Starship fuel costs 500 Cr per ton (refined) or 100 Cr per ton
    # (unrefined) at most starports.
    # A power plant, to provide power for one trip ... requires fuel
    # in accordance with the formula 10 * Pn, where Pn is the power plant
    # size rating. The formula indicates the amount of fuel in tons, and
    # all such fuel is consumed in the process of a normal trip.
    # A jump drive requires fuel to make one jump (regardless of jump
    # number) based on the formula 0.1 * M * Jn, where M equals the mass
    # displacement of the ship and Jn equals the jump number of the drive.
    # Book 2 p. 19
    # Using the type 200 hull, the free trader...
    # Jump drive-A, maneuver drive-A and power plant-A are all installed...
    # giving the starship capability for acceleration of 1G and jump-1.
    # Fuel tankage for 30 tons...

    # From this, trip fuel usage is 10 tons, and jump-1 is 20 tons. The
    # ship empties its tanks every trip.
    def refuel(self) -> str:
        """Refuel the Ship."""
        if self._starport in ('E', 'X'):
            raise GuardClauseFailure(f"No fuel is available at starport {self._starport}.")

        if self._starport not in ("A", "B"):
            per_ton = 100
            fuel_quality = "unrefined"
            self.message_views("Note: only unrefined fuel available at this facility.")
        else:
            per_ton = 500
            fuel_quality = "refined"

        amount = self.fuel_tank_size() - self.fuel_level()
        price = Credits(amount * per_ton)

        confirm = self.get_input('confirm', f"Purchase {amount} tons of fuel for {price}? ")
        if confirm == 'n':
            return ""

        self.message_views(f"Charging {price} for refuelling.")

        self._fill_tanks(fuel_quality)
        self.financials.debit(price, "refuelling")
        return "Your ship is fully refuelled."

    # Book 2 p. 35
    # Unrefined fuel may be obtained by skimming the atmosphere of a
    # gas giant if unavailable elsewhere. Most star systems have at
    # least one...
    #
    # Traveller '77 does not restrict this to streamlined ships, and
    # also does not include ocean refuelling, but I think I will be
    # including both options. (In all likelihood this will lean heavily
    # toward second edition...)

    # TO_DO: is it worth restricting by location too? (jump)
    def skim(self) -> str:
        """Refuel the Ship by skimming from a gas giant planet."""
        if not self._gas_giant:
            if self._in_deep_space():
                raise GuardClauseFailure("You are stranded in deep space." +
                                         "No fuel skimming possible.")
            raise GuardClauseFailure("There is no gas giant in this system." +
                                     "No fuel skimming possible.")

        if not self.ship.model.streamlined:
            raise GuardClauseFailure("Your ship is not streamlined and cannot skim fuel.")

        if not self._can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")

        self._fill_tanks("unrefined")
        self._add_day()
        return "Your ship is fully refuelled."

    # TO_DO: is it worth restricting by location too? (wilderness)
    def wilderness_refuel(self) -> str:
        """Refuel the Ship from open water on the world's surface."""
        if cast(StarSystem, self.map_hex).hydrographics == 0:
            raise GuardClauseFailure("No water available on this planet.")

        self._fill_tanks("unrefined")
        self._add_day()
        return "Your ship is fully refuelled."

    def jump_systems_check(self) -> str:
        """Verify the Ship is ready to perform a hyperspace jump."""
        self.ship.check_failure_pre_jump(self.maintenance_status())

        if not self._can_jump():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot perform jump.{END_FORMAT}")

        if not self.ship.sufficient_jump_fuel():
            raise GuardClauseFailure(self.ship.insufficient_jump_fuel_message())

        if not self.ship.sufficient_life_support():
            raise GuardClauseFailure(self.ship.insufficient_life_support_message())

        return "All systems ready for jump."

    def misjump_check(self, destination: Coordinate) -> str:
        """Test for misjump and report results."""
        if self.tanks_are_polluted():
            modifier = 3
        else:
            modifier = -1
        if self.maintenance_status() == "red":
            modifier += 2

        misjump_check = die_roll(2) + modifier
        if misjump_check > 11:
            misjump_target, distance = get_misjump_target(self.coordinate)

            self.set_hex(self.get_system_at_coordinate(misjump_target))
            self.set_system_at_coordinate(misjump_target, self.get_star_system())

            return f"{BOLD_RED}MISJUMP!{END_FORMAT}\n" +\
                   f"{misjump_target} at distance {distance}"

        self.set_hex(self.get_system_at_coordinate(destination))
        return f"{BOLD_GREEN}Successful jump to {self.system_name()}{END_FORMAT}"

    def perform_jump(self) -> str:
        """Perform a hyperspace jump to the specified destination."""
        self.message_views(self.jump_systems_check())

        jump_range = self.ship.model.jump_range
        self.message_views(f"Systems within jump-{jump_range}:")
        destinations = self._destinations
        for i,entry in enumerate(destinations):
            self.message_views(f"{i} - {entry}")

        choice = -1
        while not 0 <= choice < len(destinations):
            choice = cast(int, self.get_input('int', "Enter destination number: "))

        coordinate = destinations[choice].coordinate
        destination = cast(StarSystem,
                           self.get_system_at_coordinate(coordinate))

        self.ship.warn_if_not_contracted(destination)

        confirmation = self.get_input('confirm', f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            return "Cancelling jump."

        self._check_unrefined_jump()

        self.message_views(f"{BOLD_RED}Executing jump!{END_FORMAT}")

        self.message_views(self.misjump_check(coordinate))

        self.set_location("jump")
        self.ship.check_failure_post_jump()
        self.set_destinations()
        self.new_depot(self.views[0])     # TO_DO: clean up muddled observer nomenclature
        self.set_financials_location(destination)
        self._consume_life_support()
        self._burn_fuel(self.ship.model.jump_fuel_cost)
        self.plus_week()
        return "Jump complete."

    def flush(self) -> str:
        """Decontaminate the Ship's fuel tanks."""
        if not self.tanks_are_polluted():
            return "Ship fuel tanks are clean. No need to flush."

        if not self._can_flush():
            return f"There are no facilities to flush tanks at starport {self._starport}."

        self._clean_fuel_tanks()
        self.plus_week()
        return "Fuel tanks have been decontaminated."

    def annual_maintenance(self) -> str:
        """Perform annual maintenance on the Ship."""
        if self._no_shipyard():
            raise GuardClauseFailure("Annual maintenance can only be performed " +
                                     "at class A or B starports.")

        cost = self.ship.maintenance_cost()
        if self.balance < cost:
            raise GuardClauseFailure("You do not have enough funds to pay for maintenance.\n"
                  f"It will cost {cost}. Your balance is {self.balance}.")

        if self.maintenance_status() == "green":
            confirmation = self.get_input('confirm', "Maintenance was performed less than " +
                                          "10 months ago. Continue (y/n)? ")
            if confirmation == "n":
                return "Cancelling maintenance."

        confirmation = self.get_input('confirm', f"Maintenance will cost {cost} and take " +
                                      "two weeks. Continue (y/n)? ")
        if confirmation == "n":
            return "Cancelling maintenance."

        self.message_views(f"Performing maintenance. Charging {cost}.")
        self.financials.last_maintenance = self.date.current_date
        self.financials.debit(cost, "annual maintenance")
        self.plus_week()
        return self.repair_ship()

    def buy_cargo(self) -> str:
        """Purchase cargo for speculative trade."""
        for i,entry in enumerate(self.cargo):
            self.message_views(f"{i} - {entry}")

        cargo = self.depot.get_cargo_lot(self.cargo, "buy")
        quantity = self._get_cargo_quantity("buy", cargo)
        if quantity is None or cargo is None:
            raise GuardClauseFailure("No cargo available for purchase.")

        if self.depot.insufficient_hold_space(cargo, quantity, self.free_cargo_space):
            raise GuardClauseFailure("There is not enough space available in the hold.")

        cost = self.depot.determine_price("purchase", cargo, quantity, self.ship.trade_skill())

        if self.depot.insufficient_funds(cost, self.balance):
            raise GuardClauseFailure("You do not have enough funds for this purchase.")

        if not self.depot.confirm_transaction("purchase", cargo, quantity, cost):
            return "Cancelling purchase."

        self.depot.remove_cargo(self.cargo, cargo, quantity)

        purchased = Cargo(cargo.name, str(quantity), cargo.price, cargo.unit_size,
                          cargo.purchase_dms, cargo.sale_dms, self.get_star_system())
        self._load_cargo([purchased])

        self.financials.debit(cost, "cargo purchase")
        self._add_day()
        return f"Successfully purchased {purchased}."

    def sell_cargo(self) -> str:
        """Sell cargo in speculative trade."""
        cargoes = [c for c in self.get_cargo_hold() if isinstance(c, Cargo)]

        if len(cargoes) == 0:
            raise GuardClauseFailure("You have no cargo on board.")

        for i,entry in enumerate(cargoes):
            self.message_views(f"{i} - {entry}")
        cargo = self.depot.get_cargo_lot(cargoes, "sell")
        if cargo is None:
            raise GuardClauseFailure("No cargo selected.")

        if self.depot.invalid_cargo_origin(cargo):
            raise GuardClauseFailure("You cannot sell cargo on its source world.")

        broker_skill = self.depot.get_broker()

        quantity = self._get_cargo_quantity("sell", cargo)
        if quantity is None:
            raise GuardClauseFailure("No cargo selected.")

        sale_price = self.depot.determine_price("sale", cargo, quantity,
                                          broker_skill + self.ship.trade_skill())

        self.financials.debit(self.depot.broker_fee(broker_skill, sale_price), "broker fee")

        if not self.depot.confirm_transaction("sale", cargo, quantity, sale_price):
            return "Cancelling purchase."

        self.depot.remove_cargo(self.get_cargo_hold(), cargo, quantity)

        self.financials.credit(sale_price, "cargo sale")
        self._add_day()
        return f"Successfully sold {cargo}."

    def load_freight(self) -> str:
        """Select and load Freight onto the Ship."""
        jump_range = self.ship.model.jump_range
        potential_destinations = self._destinations
        destinations = self.get_destinations(potential_destinations,
                                              jump_range, "freight shipments")
        if not destinations:
            return "No destinations available."

        coordinate, available = self.depot.get_available_freight(destinations)
        if available is None:
            return "No freight available."

        destination = cast(StarSystem,
                           self.get_system_at_coordinate(cast(Coordinate, coordinate)))
        self.message_views(f"Freight shipments for {destination.name}")
        self.message_views(f"{available}")

        total_tonnage, selection = self._select_freight_lots(available, destination)

        if total_tonnage == 0:
            return "No freight shipments selected."
        self.message_views(f"{total_tonnage} tons selected.")

        confirmation = self.get_input('confirm', f"Load {total_tonnage} tons of freight? (y/n)? ")
        if confirmation == 'n':
            return "Cancelling freight selection."

        for entry in selection:
            self.depot.freight[destination].remove(entry)
            self._load_cargo([Freight(entry, self.get_star_system(), destination)])
        self._add_day()
        return f"Successfully loaded {total_tonnage} tons of Freight for {destination}."

    def unload_freight(self) -> str:
        """Unload Freight from the Ship and receive payment."""
        if self.ship.destination is None:
            raise GuardClauseFailure("You have no contracted destination.")

        freight = self._get_freight()
        if len(freight) == 0:
            raise GuardClauseFailure("You have no freight on board.")

        if self.ship.destination != self.get_star_system():
            raise GuardClauseFailure(f"{BOLD_RED}You are not at the contracted " +\
                                     "destination for this freight.\n" +\
                                     "It should be unloaded at "
                                     f"{self._destination_name}.{END_FORMAT}")

        freight_tonnage = sum(f.tonnage for f in freight)
        self._remove_all_freight()

        payment = Credits(1000 * freight_tonnage)
        self.financials.credit(payment, "freight shipment")
        self._add_day()

        return f"Receiving payment of {payment} for {freight_tonnage} tons shipped."

    def get_destinations(self, potential_destinations: List[StarSystem],
                         jump_range: int, prompt: str) -> List[StarSystem]:
        """Return a list of all reachable destinations with Freight or Passengers."""
        result: List[StarSystem] = []
        if self.ship.destination is not None:
            if self.ship.destination == self.get_star_system():
                self.message_views(f"{BOLD_RED}There is still freight to be unloaded "
                      f"on {self.system_name()}.{END_FORMAT}")
                return result
            if self.ship.destination in potential_destinations:
                self.message_views(f"You are under contract. Only showing {prompt} for " +
                      f"{self._destination_name}:\n")
                result = [cast(StarSystem, self.ship.destination)]
            else:
                self.message_views(f"You are under contract to {self._destination_name} " +
                      "but it is not within jump range of here.")

        else:
            self.message_views(f"Available {prompt} within jump-{jump_range}:\n")
            result = potential_destinations

        return result

    def book_passengers(self) -> str:
        """Book passengers for travel to a destination."""
        jump_range = self.ship.model.jump_range
        potential_destinations = self._destinations
        destinations = self.get_destinations(potential_destinations,
                                              jump_range, "passengers")
        if not destinations:
            return "No destinations available."

        coordinate, available = self.depot.get_available_passengers(destinations)
        if available is None:
            return "No freight available."

        destination = cast(StarSystem,
                           self.get_system_at_coordinate(coordinate))
        self.message_views(f"Passengers for {destination.name} (H,M,L): {available}")

        selection = self._select_passengers(available, destination)

        if selection == (0,0,0):
            return "No passengers selected."
        self.message_views(f"Selected (H, M, L): {selection}")

        confirmation = self.get_input('confirm', f"Book {selection} passengers? (y/n)? ")
        if confirmation == 'n':
            return "Cancelling passenger selection."

        # TO_DO: need to consider the case where we already have passengers
        #        Probably want to wrap passenger field access in a property...
        high = [Passenger(Passage.HIGH, destination)
                for _ in range(selection[Passage.HIGH.value])]
        baggage = [Baggage(self.get_star_system(), destination)
                   for _ in range(selection[Passage.HIGH.value])]
        middle = [Passenger(Passage.MIDDLE, destination)
                  for _ in range(selection[Passage.MIDDLE.value])]
        low = [Passenger(Passage.LOW, destination)
               for _ in range(selection[Passage.LOW.value])]

        self._add_passengers(high)
        self._load_cargo(baggage)        #type: ignore[arg-type]
        self._add_passengers(middle)
        self._add_passengers(low)
        self._remove_passengers_from_depot(destination, selection)

        return f"Successfully booked {self.ship.total_passenger_count} " +\
                f"passengers for {destination}."

    def recharge_life_support(self) -> None:
        """Recharge the Ship's life support system."""
        self.financials.debit(self.ship.recharge(), "life support")

    # TERMINAL ==========================================
    def _valid_input(self, tokens: List[str]) -> Tuple[int | None, str | None]:
        """Validate passenger selection input."""
        if len(tokens) != 2:
            self.message_views("Please enter in the format: passage number (example: h 5).")
            return None, None

        passage = tokens[0]
        if passage not in ['h', 'm', 'l']:
            self.message_views("Please enter 'h', 'm' or 'l' for passage class.")
            return None, None

        try:
            count = int(tokens[1])
        except ValueError:
            self.message_views("Please input a number.")
            return None, None

        return count, passage

    # pylint: disable=R0913
    # R0913: too many arguments (6/5)
    def _sufficient_quantity(self, passage: str, available: int,
                            capacity: int, count: int, hold: int) -> bool:
        """Test whether there are enough berths/passengers to book."""
        if available - count < 0:
            self.message_views(f"There are not enough {passage} passengers available.")
            return False

        if capacity - count < 0:
            berths = "staterooms"
            if passage == "low":
                berths = "low berths"
            self.message_views(f"There are not enough {berths} available.")
            return False

        if passage == "high":
            if hold - count < 0:
                self.message_views("There is not enough cargo space available.")
                return False

        return True

    def _select_passengers(self, available: Tuple[int, ...],
                          destination: Hex) -> Tuple[int, ...]:
        """Select Passengers from a list of available candidates."""
        selection: Tuple[int, ...] = (0,0,0)
        ship_capacity: Tuple[int, ...] = (self.ship.empty_passenger_berths,
                                          self.ship.empty_low_berths)
        ship_hold = self.free_cargo_space

        while True:
            if available == (0,0,0):
                self.message_views(f"No more passengers available for {destination.name}.")
                break

            # can't use int input here since we allow for 'q' as well...
            response = self.get_input("", "Choose a passenger by type (h, m, l) " +
                                                     "and number, or q to exit): ")
            if response == 'q':
                break

            tokens = cast(str, response).split()
            count, passage = self._valid_input(tokens)
            if not count:
                continue

            suffix = get_plural_suffix(count)

            # pylint: disable=E1130
            # E1130: bad operand type for unary-: NoneType
            match passage:
                case 'h':
                    if not self._sufficient_quantity("high", available[0],
                                                ship_capacity[0], count, ship_hold):
                        continue
                    self.message_views(f"Adding {count} high passenger{suffix}.")
                    selection = tuple(a+b for a,b in zip(selection,(count,0,0)))
                    available = tuple(a+b for a,b in zip(available,(-count,0,0)))
                    ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-count,0)))
                    ship_hold -= count

                case 'm':
                    if not self._sufficient_quantity("middle", available[1],
                                                ship_capacity[0], count, ship_hold):
                        continue
                    self.message_views(f"Adding {count} middle passenger{suffix}.")
                    selection = tuple(a+b for a,b in zip(selection,(0,count,0)))
                    available = tuple(a+b for a,b in zip(available,(0,-count,0)))
                    ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-count,0)))

                case 'l':
                    if not self._sufficient_quantity("low", available[2],
                                                ship_capacity[1], count, ship_hold):
                        continue
                    self.message_views(f"Adding {count} low passenger{suffix}.")
                    selection = tuple(a+b for a,b in zip(selection,(0,0,count)))
                    available = tuple(a+b for a,b in zip(available,(0,0,-count)))
                    ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(0,-count)))

            self.message_views("")
            self.message_views(f"Remaining (H, M, L): {available}")
            self.message_views(f"Selected (H, M, L): {selection}")
            self.message_views(f"Empty ship berths (H+M, L): {ship_capacity}\n")

        self.message_views("Done selecting passengers.")
        return selection

    # DEPOT =============================================
    def new_depot(self, view: Any) -> None:
        """Create a new CargoDepot attached to the current game state."""
        self.depot = CargoDepot(self.get_star_system(), self.date.current_date)
        self.depot.add_view(view)
        self.depot.controls = view

    @property
    def cargo(self) -> List[Cargo]:
        """Return a list of Cargo available at the current StarSystem's CargoDepot."""
        return self.depot.cargo

    def _get_cargo_quantity(self, prompt: str, cargo: Cargo | None) -> int | None:
        """Get a quantify of Cargo from the player to sell or purchase."""
        if cargo:
            return self.depot.get_cargo_quantity(prompt, cargo)
        return None

    def _remove_passengers_from_depot(self, destination: StarSystem,
                                     selection: Tuple[int, ...]) -> None:
        """Remove the selection from the available passengers at the CargoDepot."""
        self.depot.passengers[destination] = tuple(a-b for a,b in
                                        zip(self.depot.passengers[destination], selection))


    def _low_lottery(self, low_lottery_amount) -> str:
        """Run the low passage lottery and apply results."""
        result = ""
        if self.low_passenger_count > 0:
            low_passengers = self._get_low_passengers()
            for passenger in low_passengers:
                if die_roll(2) + passenger.endurance + self.ship.medic_skill() < 5:
                    passenger.survived = False

            survivors = [p for p in low_passengers if p.survived]
            result += f"{len(survivors)} of {len(low_passengers)} low passengers survived revival."

            winner = False
            for passenger in low_passengers:
                if passenger.guess == len(survivors) and passenger.survived:
                    winner = True

            if not winner:
                result += "\nNo surviving low lottery winner. "
                result += f"The captain is awarded {low_lottery_amount}."
                self.financials.credit(low_lottery_amount, "low lottery")

        return result


    def _select_freight_lots(self, available: List[int],
                             destination: Hex) -> Tuple[int, List[int]]:
        """Select Freight lots from a list of available shipments."""
        selection: List[int] = []
        total_tonnage = 0
        hold_tonnage = self.free_cargo_space
        while True:
            if len(available) == 0:
                self.message_views(f"No more freight available for {destination.name}.")
                break

            # can't use int input here since we allow for 'q' as well...
            response: int | str = self.get_input("", "Choose a shipment by tonnage ('q' to exit): ")
            if response == 'q':
                break

            try:
                response = int(response)
            except ValueError:
                self.message_views("Please input a number.")
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
                    self.message_views(f"{available}")
                    self.message_views(f"Cargo space left: {hold_tonnage}")
                else:
                    self.message_views(f"{BOLD_RED}That shipment will not " +
                                       f"fit in your cargo hold.{END_FORMAT}")
                    self.message_views(f"{BOLD_RED}Hold free space: {hold_tonnage}{END_FORMAT}")
            else:
                self.message_views(f"{BOLD_RED}There are no shipments of " +
                                   f"size {response}.{END_FORMAT}")

        self.message_views("Done selecting shipments.")
        return (total_tonnage, selection)

    # FINANCIALS ========================================
    @property
    def balance(self) -> Credits:
        """Return current account balance."""
        return self.financials.balance

    def load_financials(self, data: str, view: Any) -> None:
        """Apply Financials from json data to Financials field."""
        self.financials = financials_from(data)
        self.financials.ship = self.ship
        self.financials.add_view(view)
        self.date.add_observer(self.financials)

    def get_ledger(self) -> List[str]:
        """Return the contents of the account ledger."""
        return self.financials.ledger

    def set_ledger(self, entries: List[str]) -> None:
        """Set the contents of the account ledger."""
        self.financials.ledger = entries

    def set_financials_location(self, location: StarSystem) -> None:
        """Set the current location of the Financials object."""
        self.financials.location = location

    def maintenance_status(self) -> str:
        """Return the current maintenance status of the Ship."""
        return self.financials.maintenance_status(self.date.current_date)

    def encode_financials(self) -> str:
        """Return a string encoding the current state of the Financials object."""
        return self.financials.encode()

    # LOCATION ==========================================
    def set_hex(self, map_hex: Hex) -> None:
        """Change the current map hex."""
        self.map_hex = map_hex

    def get_star_system(self) -> StarSystem:
        """Return the current StarSystem."""
        return cast(StarSystem, self.map_hex)

    def system_name(self) -> str:
        """Return the name of the current StarSystem."""
        return self.map_hex.name

    @property
    def coordinate(self) -> Coordinate:
        """Return the Coordinate of the current MapHex."""
        return self.map_hex.coordinate

    @property
    def description(self) -> str:
        """Return the descriptor for the current location within the MapHex."""
        return self.map_hex.description()

    @property
    def _starport(self) -> str:
        """Return the classification of the current location's starport."""
        return cast(StarSystem, self.map_hex).starport

    @property
    def _gas_giant(self) -> bool:
        """Return whether the StarSystem contains a gas giant planet or not."""
        return cast(StarSystem, self.map_hex).gas_giant

    @property
    def _at_starport(self) -> bool:
        """Return whether the Ship is currently berthed at the mainworld's starport."""
        return cast(StarSystem, self.map_hex).at_starport()

    def set_location(self, location: str) -> None:
        """Change the location within the current map hex."""
        cast(StarSystem, self.map_hex).location = location

    def _can_flush(self) -> bool:
        """Test whether facilities to flush fuel tanks are present at the current location."""
        return self._starport in ('A', 'B', 'C', 'D')

    def _no_shipyard(self) -> bool:
        """Test whether maintenance can be performed at the current location."""
        return self._starport not in ('A', 'B')

    def _in_deep_space(self) -> bool:
        """Test whether the Ship is currently in a DeepSpace Hex."""
        return isinstance(self.map_hex, DeepSpace)

    @property
    def _destinations(self) -> List[StarSystem]:
        """Return a list of StarSystems reachable from the current MapHex."""
        return self.map_hex.destinations.copy()

    # TO_DO: shouldn't this be a property setter?
    def set_destinations(self) -> None:
        """Determine and save the StarSystems within jump range of the current MapHex."""
        jump_range = self.ship.model.jump_range
        self.map_hex.destinations = self.star_map.get_systems_within_range(self.coordinate,
                                                                           jump_range)

    # STAR MAP ==========================================
    def new_star_map(self, systems: Dict[Coordinate, Hex]) -> None:
        """Create a new StarMap."""
        self.star_map = StarMap(systems)

    def get_all_hexes(self) -> Dict[Coordinate, Hex]:
        """Return a dictionary of all Hexes in the StarMap, keyed by Coordinate."""
        return self.star_map.systems

    def _get_all_systems(self) -> List[StarSystem]:
        """Return a list of all StarSystem contained in the StarMap."""
        return self.star_map.get_all_systems()

    def list_map(self) -> List[str]:
        """Return a list of all Hexes in the map, as strings."""
        return self.star_map.list_map()

    def get_system_at_coordinate(self, coord: Coordinate) -> Hex:
        """Return the Hex at the specified coordinate, or create it."""
        return self.star_map.get_system_at_coordinate(coord)

    def set_system_at_coordinate(self, coord: Coordinate, map_hex: Hex) -> None:
        """Set the specified coordinate in the StarMap to the specified Hex object."""
        self.star_map.systems[coord] = map_hex

    def get_subsector_string(self, map_hex: Hex) -> str:
        """Return the subsector coordinates for a given StarSystem."""
        return self.star_map.get_subsector_string(map_hex)

    def get_all_subsectors(self) -> Dict[Tuple[int, int], Subsector]:
        """Return a dictionary of all Subsectors in the StarMap, keyed by coordinate."""
        return self.star_map.subsectors

    def get_coords_in_subsector(self, sub_coord: Tuple[int,int]) -> List[Coordinate]:
        """Return a list of all Coordinates in the specified subsector."""
        return self.star_map.get_systems_in_subsector(sub_coord)

    def get_subsector_at_coordinate(self, sub_coord: Tuple[int,int]) -> Subsector:
        """Return the Subsector at the specified coordinate."""
        return self.star_map.subsectors[sub_coord]

    def set_subsector_at_coordinate(self, sub_coord: Tuple[int,int], sub: Subsector) -> None:
        """Set the specified coordinate in the StarMap to the specified Subsector object."""
        self.star_map.subsectors[sub_coord] = sub

    def get_system_strings(self) -> Tuple[List[str], str]:
        """Return a list of strings describing all known StarSystems."""
        systems = self._get_all_systems()
        system_strings = []
        highlight = ""
        for sys in systems:
            combined = f"{self.get_subsector_string(sys)} : {sys}"
            system_strings.append(combined)
            if sys == self.get_star_system():
                highlight = combined
        return (system_strings, highlight)

    # SHIP ==============================================
    def new_ship(self, ship_details: str, ship_model: str, view: Any) -> None:
        """Create a new Ship."""
        self.ship = ship_from(ship_details, ship_model)
        self.ship.add_view(view)
        self.ship.controls = view

    def encode_ship(self) -> str:
        """Return a string encoding the current state of the Ship."""
        return self.ship.encode()

    def ship_string(self) -> str:
        """Return the string representation of the Ship."""
        return str(self.ship)

    def ship_model_name(self) -> str:
        """Return the name of the Ship's Model."""
        return self.ship.model.name

    @property
    def _destination_name(self) -> str:
        """Return the name of the Ship's destination."""
        if self.ship.destination:
            return self.ship.destination.name
        return "None"

    @property
    def life_support_level(self) -> int:
        """Return the current life support level of the Ship."""
        return self.ship.life_support_level

    def _consume_life_support(self) -> None:
        """Reduce life support supplies consumed during travel."""
        self.ship.life_support_level = 0

    def _check_unrefined_jump(self) -> None:
        """Track hyperspace jumps performed with unrefined fuel."""
        if self.tanks_are_polluted():
            self.ship.unrefined_jump_counter += 1

    def tanks_are_polluted(self) -> bool:
        """Test whether the Ship's fuel tanks have been polluted by unrefined fuel."""
        return self.ship.fuel_quality == FuelQuality.UNREFINED

    def _clean_fuel_tanks(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        self.ship.fuel_quality = FuelQuality.REFINED
        self.ship.unrefined_jump_counter = 0

    def _leg_fuel_cost(self) -> int:
        """Return the amount of fuel used in one leg of trip, in tons."""
        return self.ship.model.trip_fuel_cost // 2

    def _burn_fuel(self, amount: int) -> None:
        """Reduce the fuel in the Ship's tanks by the specified amount."""
        self.ship.current_fuel -= amount

    def _tanks_are_full(self) -> bool:
        """Test whether the Ship's fuel tanks are full or not."""
        return self.fuel_level() == self.fuel_tank_size()

    def fuel_level(self) -> int:
        """Return the current amount of fuel in the Ship's tanks."""
        return self.ship.current_fuel

    # TO_DO: this would be better as a boolean test
    def _check_fuel_level(self) -> int | None:
        """Verify there is sufficient fuel in the tanks to make a trip."""
        if self.fuel_level() < self._leg_fuel_cost():
            return None
        return self._leg_fuel_cost()

    def fuel_tank_size(self) -> int:
        """Return the capacity of the Ship's fuel tanks."""
        return self.ship.model.fuel_tank

    def _fill_tanks(self, quality: str="refined") -> None:
        """Fill the Ship's fuel tanks to their full capacity."""
        if self._tanks_are_full():
            raise GuardClauseFailure("Fuel tank is already full.")

        self.ship.current_fuel = self.fuel_tank_size()
        if quality == "unrefined":
            self.ship.fuel_quality = FuelQuality.UNREFINED

    def _can_maneuver(self) -> bool:
        """Test whether the Ship can travel to a destination."""
        return self.ship.repair_status != RepairStatus.BROKEN

    def _can_jump(self) -> bool:
        """Test whether the Ship can perform a hyperspace jump."""
        return self.ship.repair_status not in (RepairStatus.BROKEN, RepairStatus.PATCHED)

    def get_repair_string(self) -> str:
        """Return a string representing current repair state of the Ship."""
        match self.ship.repair_status:
            case RepairStatus.BROKEN:
                return "\tDRIVE FAILURE - UNABLE TO JUMP OR MANEUVER"
            case RepairStatus.PATCHED:
                return "\tSEEK REPAIRS - UNABLE TO JUMP"
            case RepairStatus.REPAIRED:
                return ""

    def get_passengers(self) -> List[Passenger]:
        """Return a list of Passengers on board the Ship."""
        return self.ship.passengers

    def _get_low_passengers(self) -> List[Passenger]:
        """Return a list of the Low Passengers on board the Ship."""
        return [p for p in self.get_passengers() if p.passage == Passage.LOW]

    def set_passengers(self, passengers: List[Passenger]) -> None:
        """Set the list of Passengers on board the Ship."""
        self.ship.passengers = passengers

    def _add_passengers(self, passengers: List[Passenger]) -> None:
        """Add a list of Passengers to those present on board the Ship."""
        self.ship.passengers += passengers

    @property
    def low_passenger_count(self) -> int:
        """Return the number of low passengers on board the Ship."""
        return self.ship.low_passenger_count

    def get_cargo_hold(self) -> List[Freight | Cargo]:
        """Return the current contents of the Ship's cargo hold."""
        return self.ship.cargo_hold()

    def passenger_manifest(self) -> str:
        """Return a string showing all Passengers on board the Ship."""
        return f"High passengers: {self.ship.high_passenger_count}\n" +\
               f"Middle passengers: {self.ship.middle_passenger_count}\n" +\
               f"Low passengers: {self.low_passenger_count}\n" +\
               f"DESTINATION: {self._destination_name}\n\n" +\
               f"Empty berths: {self.ship.empty_passenger_berths}\n" +\
               f"Empty low berths: {self.ship.empty_low_berths}"

    def set_cargo_hold(self, contents: List[Freight | Cargo]) -> None:
        """Set the contents of the Ship's cargo hold."""
        self.ship.hold = contents

    def _load_cargo(self, cargo: List[Cargo | Freight]) -> None:
        """Load the specified cargo into the Ship's hold."""
        for item in cargo:
            self.ship.load_cargo(item)

    @property
    def free_cargo_space(self) -> int:
        """Return the amount of free space in the Ship's cargo hold, in displacent tons."""
        return self.ship.free_space()

    def _remove_baggage(self) -> None:
        """Unload all Baggage from the Ship's cargo hold."""
        self.ship.hold = [item for item in self.ship.hold
                          if not isinstance(item, Baggage)]

    def _get_freight(self) -> List[Freight]:
        """Return a list of all Freight in the Ship's cargo hold."""
        return [f for f in self.get_cargo_hold() if isinstance(f, Freight)]

    # TO_DO: also removes Baggage - should not be any on board when this
    #        method is called, but still...
    def _remove_all_freight(self) -> None:
        """Unload all Freight from the Ship's cargo hold."""
        self.ship.hold = [item for item in self.ship.hold
                          if not isinstance(item, Freight)]

    def get_crew(self) -> List[Crew]:
        """Return a list of the Ship's Crew."""
        return self.ship.crew

    # DATE ==============================================
    @property
    def date_string(self) -> str:
        """Return the current date as a string."""
        return f"{self.date}"

    def _add_day(self) -> None:
        """Advance the Calendar by a day."""
        self.date.day += 1

    def plus_week(self) -> None:
        """Move the current day forward by seven days."""
        self.date.plus_week()

    def load_calendar(self, data: str) -> None:
        """Apply date from json data to Game calendar field."""
        self.date = Calendar()
        modify_calendar_from(self.date, data)

    def attach_date_observers(self) -> None:
        """Attach observers to Calendar field."""
        self.date.add_observer(self.depot)
        self.date.add_observer(self.financials)

class Error(Exception):
    """Base class for all exceptions raised by this module."""

class GuardClauseFailure(Error):
    """A guard clause in the method did not pass."""
