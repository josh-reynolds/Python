"""Contains the game simulation model with references to all component objects.

Model - contains references to all game model objects.
"""
from typing import List, Any, cast, Sequence
from src.baggage import Baggage
from src.calendar import Calendar, modify_calendar_from
from src.cargo import Cargo
from src.cargo_depot import CargoDepot
from src.coordinate import Coordinate
from src.credits import Credits
from src.financials import Financials, financials_from
from src.imperial_date import ImperialDate
from src.passengers import Passenger, Passage
from src.ship import Ship, RepairStatus, FuelQuality, ship_from
from src.star_system import StarSystem, Hex, DeepSpace
from src.star_map import StarMap
from src.utilities import die_roll

# pylint: disable=R0904
# R0904: too many public methods (21/20)
class Model:
    """Contains references to all game model objects."""

    def __init__(self) -> None:
        """Create an instance of a Model object."""
        self.date: Calendar
        self.ship: Ship
        self.star_map: StarMap
        self.map_hex: Hex
        self.financials: Financials
        self.depot: CargoDepot

    def __repr__(self) -> str:
        """Return the developer string representation of the Model object."""
        return "Model()"

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

    def refuel(self) -> str:
        """Refuel the Ship."""
        if self.starport in ('E', 'X'):
            return f"No fuel is available at starport {self.starport}."

        cost = self.ship.refuel(self.starport)
        self.financials.debit(cost, "refuelling")
        return "Your ship is fully refuelled."

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

    def remove_freight(self, destination: StarSystem, lot: int) -> None:
        """Remove the specified Freight lot from the destination list."""
        self.depot.freight[destination].remove(lot)

    def get_available_freight(self,
                              destinations: Sequence[StarSystem]
                              ) -> tuple[Coordinate | None, list[Any] | None]:
        """Present a list of worlds and Freight shipments for the player to choose from."""
        return self.depot.get_available_freight(destinations)

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
    def on_surface(self) -> bool:
        """Return whether the Ship is currently on the surface of the mainworld."""
        return cast(StarSystem, self.map_hex).on_surface()

    def set_location(self, location: str) -> None:
        """Change the location within the current map hex."""
        cast(StarSystem, self.map_hex).detail = location

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
    def get_system_at_coordinate(self, coord: Coordinate) -> Hex:
        """Return the contents of the specified coordinate, or create it."""
        return self.star_map.get_system_at_coordinate(coord)

    # SHIP ==============================================
    def new_ship(self, ship_details: str, ship_model: str, observer: Any) -> None:
        """Create a new Ship."""
        self.ship = ship_from(ship_details, ship_model)
        self.ship.add_observer(observer)
        self.ship.controls = observer

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

    @property
    def jump_range(self) -> int:
        """Return the jump range of the Ship (in parsecs)."""
        return self.ship.model.jump_range

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

    def burn_fuel(self, amount: int) -> None:
        """Reduce the fuel in the Ship's tanks by the specified amount."""
        self.ship.current_fuel -= amount

    def tanks_are_full(self) -> bool:
        """Test whether the Ship's fuel tanks are full or not."""
        return self.fuel_level() == self.ship.model.fuel_tank

    def fuel_level(self) -> int:
        """Return the current amount of fuel in the Ship's tanks."""
        return self.ship.current_fuel

    def fill_tanks(self, quality: str="refined") -> None:
        """Fill the Ship's fuel tanks to their full capacity."""
        self.ship.current_fuel = self.ship.model.fuel_tank
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

    @property
    def free_cargo_space(self) -> int:
        """Return the amount of free space in the Ship's cargo hold, in displacent tons."""
        return self.ship.free_space()

    def remove_baggage(self) -> None:
        """Unload all Baggage from the Ship's cargo hold."""
        self.ship.hold = [item for item in self.ship.hold
                          if not isinstance(item, Baggage)]

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
