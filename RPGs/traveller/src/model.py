"""Contains the game simulation model with references to all component objects.

Model - contains references to all game model objects.

Error - base class for exceptions thrown from this module.

GuardClauseFailure - thrown when a guard clause in the method did not pass.
"""
from typing import List, Any, cast, Sequence, Dict, Tuple
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
from src.imperial_date import ImperialDate
from src.passengers import Passenger, Passage
from src.ship import Ship, RepairStatus, FuelQuality, ship_from
from src.star_system import StarSystem, Hex, DeepSpace
from src.star_map import StarMap
from src.subsector import Subsector
from src.utilities import die_roll, pr_list

# pylint: disable=R0904, R0902
# R0904: too many public methods (21/20)
# R0902: too many instance attributes (8/7)
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

        self.observers: List[Any] = [controls]
        self.controls = controls

    def __repr__(self) -> str:
        """Return the developer string representation of the Model object."""
        return "Model()"

    def get_input(self, constraint: str, prompt: str) -> str | int:
        """Request input from controls."""
        return self.controls.get_input(constraint, prompt)    # type: ignore[union-attr]

    def add_observer(self, observer: Any) -> None:
        """Add an observer to respond to UI messages."""
        self.observers.append(observer)

    def message_observers(self, message: str, priority: str="") -> None:
        """Pass a message on to all observers."""
        for observer in self.observers:
            observer.on_notify(message, priority)

    # TRANSITIONS =======================================
    def inbound_from_jump(self) -> str:
        """Move from the jump point to orbit."""
        if self.in_deep_space():
            raise GuardClauseFailure(f"{BOLD_RED}You are in deep space. " +\
                           f"There is no inner system to travel to.{END_FORMAT}")

        if not self.can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot travel " +\
                                      "to orbit.{END_FORMAT}")

        leg_fc = self.check_fuel_level()
        if not leg_fc:
            raise GuardClauseFailure("Insufficient fuel to travel in from the jump point.")

        self.burn_fuel(leg_fc)
        self.add_day()
        self.set_location("orbit")
        return "Successfully travelled in to orbit."

    def outbound_to_jump(self) -> str:
        """Move from orbit to the jump point."""
        if not self.can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot " +\
                                     f"travel to the jump point.{END_FORMAT}")

        leg_fc = self.check_fuel_level()
        if not leg_fc:
            raise GuardClauseFailure("Insufficient fuel to travel out to the jump point.")

        self.burn_fuel(leg_fc)
        self.add_day()
        self.set_location("jump")
        return "Successfully travelled out to the jump point."

    # TO_DO: should merge with wilderness()
    def land(self) -> str:
        """Move from orbit to the starport."""
        if not self.streamlined:
            raise GuardClauseFailure("Your ship is not streamlined and cannot land.")

        if not self.can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot land.{END_FORMAT}")

        result = ""
        if self.destination() == self.get_star_system():
            if self.total_passenger_count > 0:
                result += f"Passengers disembarking on {self.system_name()}.\n"

                funds = Credits(sum(p.ticket_price.amount for p in \
                        self.get_passengers()))
                low_lottery_amount = Credits(10) * self.low_passenger_count
                funds -= low_lottery_amount
                result += f"Receiving {funds} in passenger fares.\n"
                self.credit(funds, "passenger fare")

                result += self.low_lottery(low_lottery_amount)

                self.set_passengers([])
                self.remove_baggage()

        self.set_location("starport")
        self.berthing_fee()
        result += f"\nLanded at the {self.system_name()} starport."""
        return result

    def wilderness(self) -> str:
        """Move from orbit to the planet's surface."""
        if not self.streamlined:
            raise GuardClauseFailure("Your ship is not streamlined and cannot land.")

        if not self.can_maneuver():
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
        if self.total_passenger_count > 0:
            passenger_string += f"Boarding {self.total_passenger_count} "
            passenger_string += f"passengers for {self.destination_name}.\n"

        if self.low_passenger_count > 0:
            low_passengers = self.get_low_passengers()
            for passenger in low_passengers:
                passenger.guess_survivors(self.low_passenger_count)

        result = passenger_string + result
        return result

    def to_orbit(self) -> str:
        """Move from the planet surface to orbit."""
        if not self.can_maneuver():
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

        self.add_day()
        if die_roll(2) + self.engineering_skill() > 9:
            self.ship.repair_status = RepairStatus.PATCHED
            return "Ship partially repaired. Visit a starport for further work."
        return "No progress today. Drives are still out of commission."

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self) -> str:
        """Fully repair damage to the Ship (Starport)."""
        if self.starport in ["D", "E", "X"]:
            return f"No repair facilities available at starport {self.starport}"

        if self.ship.repair_status == RepairStatus.REPAIRED:
            return "Your ship is not damaged."

        self.ship.repair_status = RepairStatus.REPAIRED
        self.clean_fuel_tanks()
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
        if self.starport in ('E', 'X'):
            raise GuardClauseFailure(f"No fuel is available at starport {self.starport}.")

        if self.starport not in ("A", "B"):
            per_ton = 100
            fuel_quality = "unrefined"
            self.message_observers("Note: only unrefined fuel available at this facility.")
        else:
            per_ton = 500
            fuel_quality = "refined"

        amount = self.fuel_tank_size() - self.fuel_level()
        price = Credits(amount * per_ton)

        confirm = self.get_input('confirm', f"Purchase {amount} tons of fuel for {price}? ")
        if confirm == 'n':
            return ""

        self.message_observers(f"Charging {price} for refuelling.")

        self.fill_tanks(fuel_quality)
        self.debit(price, "refuelling")
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
        if not self.gas_giant:
            if self.in_deep_space():
                raise GuardClauseFailure("You are stranded in deep space." +
                                         "No fuel skimming possible.")
            raise GuardClauseFailure("There is no gas giant in this system." +
                                     "No fuel skimming possible.")

        if not self.streamlined:
            raise GuardClauseFailure("Your ship is not streamlined and cannot skim fuel.")

        if not self.can_maneuver():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot skim fuel.{END_FORMAT}")

        self.fill_tanks("unrefined")
        self.add_day()
        return "Your ship is fully refuelled."

    # TO_DO: is it worth restricting by location too? (wilderness)
    def wilderness_refuel(self) -> str:
        """Refuel the Ship from open water on the world's surface."""
        if cast(StarSystem, self.map_hex).hydrographics == 0:
            raise GuardClauseFailure("No water available on this planet.")

        self.fill_tanks("unrefined")
        self.add_day()
        return "Your ship is fully refuelled."

    def jump_systems_check(self) -> str:
        """Verify the Ship is ready to perform a hyperspace jump."""
        self.check_failure_pre_jump(self.maintenance_status())

        if not self.can_jump():
            raise GuardClauseFailure(f"{BOLD_RED}Drive failure. Cannot perform jump.{END_FORMAT}")

        if not self.sufficient_jump_fuel():
            raise GuardClauseFailure(self.insufficient_jump_fuel_message())

        if not self.sufficient_life_support():
            raise GuardClauseFailure(self.insufficient_life_support_message())

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
        return f"{BOLD_GREEN}Successful jump to {self.system_name}{END_FORMAT}"

    # TO_DO: remove pr_list usage, replace w/ observer
    # TO_DO: remove observer argument
    def perform_jump(self, observer: Any) -> str:
        """Perform a hyperspace jump to the specified destination."""
        self.message_observers(self.jump_systems_check())

        jump_range = self.jump_range
        self.message_observers(f"Systems within jump-{jump_range}:")
        destinations = self.destinations
        pr_list(destinations)

        choice = -1
        while not 0 <= choice < len(destinations):
            choice = cast(int, self.get_input('int', "Enter destination number: "))

        coordinate = destinations[choice].coordinate
        destination = cast(StarSystem,
                           self.get_system_at_coordinate(coordinate))

        self.warn_if_not_contracted(destination)

        confirmation = self.get_input('confirm', f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            return "Cancelling jump."

        self.check_unrefined_jump()

        self.message_observers(f"{BOLD_RED}Executing jump!{END_FORMAT}")

        self.message_observers(self.misjump_check(coordinate))

        self.set_location("jump")
        self.check_failure_post_jump()
        self.set_destinations()
        self.new_depot(observer)
        self.set_financials_location(destination)
        self.consume_life_support()
        self.burn_fuel(self.jump_fuel_cost())
        self.plus_week()
        return "Jump complete."

    def flush(self) -> str:
        """Decontaminate the Ship's fuel tanks."""
        if not self.tanks_are_polluted():
            return "Ship fuel tanks are clean. No need to flush."

        if not self.can_flush():
            return f"There are no facilities to flush tanks at starport {self.starport}."

        self.clean_fuel_tanks()
        self.plus_week()
        return "Fuel tanks have been decontaminated."

    # DEPOT =============================================
    def new_depot(self, observer: Any) -> None:
        """Create a new CargoDepot attached to the current game state."""
        self.depot = CargoDepot(self.get_star_system(), self.get_current_date())
        self.depot.add_observer(observer)
        self.depot.controls = observer

    @property
    def cargo(self) -> List[Cargo]:
        """Return a list of Cargo available at the current StarSystem's CargoDepot."""
        return self.depot.cargo

    # TO_DO: overlap with choose_from()
    def get_cargo_lot(self, source: List[Cargo], prompt: str) -> Cargo | None:
        """Select a Cargo lot from a list."""
        return self.depot.get_cargo_lot(source, prompt)

    def get_cargo_quantity(self, prompt: str, cargo: Cargo) -> int | None:
        """Get a quantify of Cargo from the player to sell or purchase."""
        return self.depot.get_cargo_quantity(prompt, cargo)

    # TO_DO: why is this in CargoDepot?
    def insufficient_funds(self, cost: Credits) -> bool:
        """Check if the player's bank balance has enough funds for a given cost."""
        return self.depot.insufficient_funds(cost, self.balance)

    def insufficient_hold_space(self, cargo: Cargo, quantity: int) -> bool:
        """Check if a given quantity of Cargo will fit in the Ship's hold."""
        return self.depot.insufficient_hold_space(cargo, quantity, self.free_cargo_space)

    def invalid_cargo_origin(self, cargo: Cargo) -> bool:
        """Restrict Cargo sale based on world of origin."""
        return self.depot.invalid_cargo_origin(cargo)

    def get_broker(self) -> int:
        """Allow player to select a broker for Cargo sales."""
        return self.depot.get_broker()

    def broker_fee(self, broker_skill: int, sale_price: Credits) -> Credits:
        """Return the broker's fee for Cargo sale."""
        return self.depot.broker_fee(broker_skill, sale_price)

    def confirm_transaction(self, prompt: str, cargo: Cargo,
                            quantity: int, price: Credits) -> bool:
        """Confirm a sale or purchase."""
        return self.depot.confirm_transaction(prompt, cargo, quantity, price)

    def determine_price(self, prompt: str,
                        cargo: Cargo, quantity: int,
                        skill: int) -> Credits:
        """Calculate the price of a Cargo transaction."""
        return self.depot.determine_price(prompt, cargo, quantity, skill)

    # TO_DO: this overlaps with ship.unload_cargo()...
    def remove_cargo(self, source: List, cargo: Cargo, quantity: int) -> None:
        """Remove cargo from a storage location."""
        self.depot.remove_cargo(source, cargo, quantity)

    def remove_freight(self, destination: StarSystem, lot: int) -> None:
        """Remove the specified Freight lot from the destination list."""
        self.depot.freight[destination].remove(lot)

    def get_available_freight(self,
                              destinations: Sequence[StarSystem]
                              ) -> tuple[Coordinate | None, list[Any] | None]:
        """Present a list of worlds and Freight shipments for the player to choose from."""
        return self.depot.get_available_freight(destinations)

    def get_available_passengers(self, destinations: Sequence[StarSystem]) -> tuple:
        """Present a list of worlds and Passengers for the player to choose from."""
        return self.depot.get_available_passengers(destinations)

    def remove_passengers_from_depot(self, destination: StarSystem,
                                     selection: Tuple[int, ...]) -> None:
        """Remove the selection from the available passengers at the CargoDepot."""
        self.depot.passengers[destination] = tuple(a-b for a,b in
                                        zip(self.depot.passengers[destination], selection))

    def low_lottery(self, low_lottery_amount) -> str:
        """Run the low passage lottery and apply results."""
        result = ""
        if self.low_passenger_count > 0:
            low_passengers = self.get_low_passengers()
            for passenger in low_passengers:
                if die_roll(2) + passenger.endurance + self.medic_skill() < 5:
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
                self.credit(low_lottery_amount, "low lottery")

        return result

    # FINANCIALS ========================================
    @property
    def balance(self) -> Credits:
        """Return current account balance."""
        return self.financials.balance

    def load_financials(self, data: str, observer: Any) -> None:
        """Apply Financials from json data to Financials field."""
        self.financials = financials_from(data)
        self.financials.ship = self.ship
        self.financials.add_observer(observer)
        self.date.add_observer(self.financials)

    def credit(self, amount: Credits, memo: str="") -> None:
        """Add the specified amount to the current account balance."""
        self.financials.credit(amount, memo)

    def debit(self, amount: Credits, memo: str="") -> None:
        """Deduct the specified amount from the current account balance."""
        self.financials.debit(amount, memo)

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
        return self.financials.maintenance_status(self.get_current_date())

    def set_maintenance_date(self) -> None:
        """Set the date annual maintenance was last performed to today."""
        self.financials.last_maintenance = self.get_current_date()

    def berthing_fee(self) -> None:
        """Deduct fee for berth at a starport from the account balance."""
        self.financials.berthing_fee(self.at_starport)

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
    def starport(self) -> str:
        """Return the classification of the current location's starport."""
        return cast(StarSystem, self.map_hex).starport

    @property
    def gas_giant(self) -> bool:
        """Return whether the StarSystem contains a gas giant planet or not."""
        return cast(StarSystem, self.map_hex).gas_giant

    @property
    def at_starport(self) -> bool:
        """Return whether the Ship is currently berthed at the mainworld's starport."""
        return cast(StarSystem, self.map_hex).at_starport()

    def set_location(self, location: str) -> None:
        """Change the location within the current map hex."""
        cast(StarSystem, self.map_hex).location = location

    def can_flush(self) -> bool:
        """Test whether facilities to flush fuel tanks are present at the current location."""
        return self.starport in ('A', 'B', 'C', 'D')

    def no_shipyard(self) -> bool:
        """Test whether maintenance can be performed at the current location."""
        return self.starport not in ('A', 'B')

    def in_deep_space(self) -> bool:
        """Test whether the Ship is currently in a DeepSpace Hex."""
        return isinstance(self.map_hex, DeepSpace)

    @property
    def destinations(self) -> List[StarSystem]:
        """Return a list of StarSystems reachable from the current MapHex."""
        return self.map_hex.destinations.copy()

    def set_destinations(self) -> None:
        """Determine and save the StarSystems within jump range of the current MapHex."""
        self.map_hex.destinations = self.star_map.get_systems_within_range(self.coordinate,
                                                                           self.jump_range)

    # STAR MAP ==========================================
    def new_star_map(self, systems: Dict[Coordinate, Hex]) -> None:
        """Create a new StarMap."""
        self.star_map = StarMap(systems)

    def get_all_hexes(self) -> Dict[Coordinate, Hex]:
        """Return a dictionary of all Hexes in the StarMap, keyed by Coordinate."""
        return self.star_map.systems

    def get_all_systems(self) -> List[StarSystem]:
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

    # SHIP ==============================================
    def new_ship(self, ship_details: str, ship_model: str, observer: Any) -> None:
        """Create a new Ship."""
        self.ship = ship_from(ship_details, ship_model)
        self.ship.add_observer(observer)
        self.ship.controls = observer

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
    def streamlined(self) -> bool:
        """Return whether the Ship is streamlined or not."""
        return self.ship.model.streamlined

    def destination(self) -> StarSystem | None:
        """Return the Ship's contracted destination, if any."""
        return self.ship.destination

    @property
    def destination_name(self) -> str:
        """Return the name of the Ship's destination."""
        if self.ship.destination:
            return self.ship.destination.name
        return "None"

    @property
    def life_support_level(self) -> int:
        """Return the current life support level of the Ship."""
        return self.ship.life_support_level

    def consume_life_support(self) -> None:
        """Reduce life support supplies consumed during travel."""
        self.ship.life_support_level = 0

    def recharge_life_support(self) -> None:
        """Recharge the Ship's life support system."""
        self.debit(self.ship.recharge(), "life support")

    @property
    def jump_range(self) -> int:
        """Return the jump range of the Ship (in parsecs)."""
        return self.ship.model.jump_range

    def warn_if_not_contracted(self, destination: StarSystem) -> None:
        """Notify the player if the choose a different jump target while under contract."""
        self.ship.warn_if_not_contracted(destination)

    def sufficient_jump_fuel(self) -> bool:
        """Test whether there is enough fuel to make a jump."""
        return self.ship.sufficient_jump_fuel()

    def insufficient_jump_fuel_message(self) -> str:
        """Return message for when there is not enough fuel for a jump."""
        return self.ship.insufficient_jump_fuel_message()

    def sufficient_life_support(self) -> bool:
        """Test whether there is enough life support for a jump."""
        return self.ship.sufficient_life_support()

    def insufficient_life_support_message(self) -> str:
        """Return message for when there is not enough life support for a jump."""
        return self.ship.insufficient_life_support_message()

    def check_failure_pre_jump(self, maintenance_status: str) -> None:
        """Test for drive failure before performing a hyperspace jump."""
        self.ship.check_failure_pre_jump(maintenance_status)

    def check_failure_post_jump(self) -> None:
        """Test for drive failure after completing a hyperspace jump."""
        self.ship.check_failure_post_jump()

    def check_unrefined_jump(self) -> None:
        """Track hyperspace jumps performed with unrefined fuel."""
        if self.tanks_are_polluted():
            self.ship.unrefined_jump_counter += 1

    def tanks_are_polluted(self) -> bool:
        """Test whether the Ship's fuel tanks have been polluted by unrefined fuel."""
        return self.ship.fuel_quality == FuelQuality.UNREFINED

    def clean_fuel_tanks(self) -> None:
        """Decontaminate the Ship's fuel tanks."""
        self.ship.fuel_quality = FuelQuality.REFINED
        self.ship.unrefined_jump_counter = 0

    def jump_fuel_cost(self) -> int:
        """Return the amount of fuel used in one hyperspace jump."""
        return self.ship.model.jump_fuel_cost

    def leg_fuel_cost(self) -> int:
        """Return the amount of fuel used in one leg of trip, in tons."""
        return self.ship.model.trip_fuel_cost // 2

    def burn_fuel(self, amount: int) -> None:
        """Reduce the fuel in the Ship's tanks by the specified amount."""
        self.ship.current_fuel -= amount

    def tanks_are_full(self) -> bool:
        """Test whether the Ship's fuel tanks are full or not."""
        return self.fuel_level() == self.fuel_tank_size()

    def fuel_level(self) -> int:
        """Return the current amount of fuel in the Ship's tanks."""
        return self.ship.current_fuel

    # TO_DO: this would be better as a boolean test
    def check_fuel_level(self) -> int | None:
        """Verify there is sufficient fuel in the tanks to make a trip."""
        if self.fuel_level() < self.leg_fuel_cost():
            return None
        return self.leg_fuel_cost()

    def fuel_tank_size(self) -> int:
        """Return the capacity of the Ship's fuel tanks."""
        return self.ship.model.fuel_tank

    def fill_tanks(self, quality: str="refined") -> None:
        """Fill the Ship's fuel tanks to their full capacity."""
        if self.tanks_are_full():
            raise GuardClauseFailure("Fuel tank is already full.")

        self.ship.current_fuel = self.fuel_tank_size()
        if quality == "unrefined":
            self.ship.fuel_quality = FuelQuality.UNREFINED

    def can_maneuver(self) -> bool:
        """Test whether the Ship can travel to a destination."""
        return self.ship.repair_status != RepairStatus.BROKEN

    def can_jump(self) -> bool:
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

    def get_low_passengers(self) -> List[Passenger]:
        """Return a list of the Low Passengers on board the Ship."""
        return [p for p in self.get_passengers() if p.passage == Passage.LOW]

    def set_passengers(self, passengers: List[Passenger]) -> None:
        """Set the list of Passengers on board the Ship."""
        self.ship.passengers = passengers

    def add_passengers(self, passengers: List[Passenger]) -> None:
        """Add a list of Passengers to those present on board the Ship."""
        self.ship.passengers += passengers

    @property
    def high_passenger_count(self) -> int:
        """Return the number of high passengers on board the Ship."""
        return self.ship.high_passenger_count

    @property
    def middle_passenger_count(self) -> int:
        """Return the number of middle passengers on board the Ship."""
        return self.ship.middle_passenger_count

    @property
    def low_passenger_count(self) -> int:
        """Return the number of low passengers on board the Ship."""
        return self.ship.low_passenger_count

    @property
    def total_passenger_count(self) -> int:
        """Return the total number of passengers on board the Ship."""
        return self.ship.total_passenger_count

    @property
    def empty_low_berths(self) -> int:
        """Return the number of unoccupied low berths on the Ship."""
        return self.ship.empty_low_berths

    @property
    def empty_passenger_berths(self) -> int:
        """Return the number of unoccupied passenger staterooms on the Ship."""
        return self.ship.empty_passenger_berths

    def get_cargo_hold(self) -> List[Freight | Cargo]:
        """Return the current contents of the Ship's cargo hold."""
        return self.ship.cargo_hold()

    def set_cargo_hold(self, contents: List[Freight | Cargo]) -> None:
        """Set the contents of the Ship's cargo hold."""
        self.ship.hold = contents

    def load_cargo(self, cargo: List[Cargo | Freight]) -> None:
        """Load the specified cargo into the Ship's hold."""
        for item in cargo:
            self.ship.load_cargo(item)

    @property
    def free_cargo_space(self) -> int:
        """Return the amount of free space in the Ship's cargo hold, in displacent tons."""
        return self.ship.free_space()

    def remove_baggage(self) -> None:
        """Unload all Baggage from the Ship's cargo hold."""
        self.ship.hold = [item for item in self.ship.hold
                          if not isinstance(item, Baggage)]

    def get_freight(self) -> List[Freight]:
        """Return a list of all Freight in the Ship's cargo hold."""
        return [f for f in self.get_cargo_hold() if isinstance(f, Freight)]

    # TO_DO: also removes Baggage - should not be any on board when this
    #        method is called, but still...
    def remove_all_freight(self) -> None:
        """Unload all Freight from the Ship's cargo hold."""
        self.ship.hold = [item for item in self.ship.hold
                          if not isinstance(item, Freight)]

    def get_crew(self) -> List[Crew]:
        """Return a list of the Ship's Crew."""
        return self.ship.crew

    def trade_skill(self) -> int:
        """Return the best trade skill from the Ship's crew."""
        return self.ship.trade_skill()

    def medic_skill(self) -> int:
        """Return the best medic skill from the Ship's crew."""
        return self.ship.medic_skill()

    def engineering_skill(self) -> int:
        """Return the best engineering skill from the Ship's crew."""
        return self.ship.engineering_skill()

    def maintenance_cost(self) -> Credits:
        """Return the annual maintenance cost for the Ship."""
        return self.ship.maintenance_cost()

    # DATE ==============================================
    def get_current_date(self) -> ImperialDate:
        """Return the Calendar's current date."""
        return self.date.current_date

    @property
    def date_string(self) -> str:
        """Return the current date as a string."""
        return f"{self.date}"

    def add_day(self) -> None:
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
