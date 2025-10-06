"""Contains the game loop and game logic for a Traveller trading simulation.

Game - contains the game loop and all game logic.
Command - represents a command available to the player.
"""
from calendar import Calendar
from random import randint, choice
from financials import Financials, Credits
from utilities import pr_yellow_on_red, int_input, confirm_input
from utilities import pr_blue, pr_red, print_list, die_roll
from ship import Ship, FuelQuality, RepairStatus
from cargo import Cargo, CargoDepot, Freight, PassageClass, Passenger, Baggage
from star_system import DeepSpace
from star_map import StarMap, StarSystemFactory

class Game:
    """Contains the game loop and all game logic."""

    def __init__(self):
        """Create an instance of Game."""
        self.running = False
        self.date = Calendar()

        self.ship = Ship()
        self.ship.load_cargo(Cargo("Grain", 20, Credits(300), 1,
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

        self.location = self.star_map.get_system_at_coordinate((0,0,0))
        coord = self.location.coordinate
        self.location.destinations = self.star_map.get_systems_within_range(coord,
                                                              self.ship.jump_range)
        self.financials = Financials(10000000, self.date.current_date, self.ship, self.location)
        self.depot = CargoDepot(self.location, self.date.current_date)

        self.date.add_observer(self.depot)
        self.date.add_observer(self.financials)

    def run(self):
        """Run the game loop."""
        self.commands = orbit   # awkward, needs to change when location ctor detail changes
        self.running = True
        while self.running:
            if self.ship.fuel_quality == FuelQuality.UNREFINED:
                fuel_quality ="(U)"
            else:
                fuel_quality = ""

            repair_state = ""
            if self.ship.repair_status == RepairStatus.BROKEN:
                repair_state = "\tDRIVE FAILURE - UNABLE TO JUMP OR MANEUVER"
            elif self.ship.repair_status == RepairStatus.PATCHED:
                repair_state = "\tSEEK REPAIRS - UNABLE TO JUMP"

            pr_yellow_on_red(f"\n{self.date} : You are " +
                             f"{self.location.description()}.{repair_state}")
            print(f"Credits: {self.financials.balance}"
                  f"\tFree hold space: {self.ship.free_space()} tons"
                  f"\tFuel: {self.ship.current_fuel}/{self.ship.fuel_tank} tons {fuel_quality}"
                  f"\tLife support: {self.ship.life_support_level}%")
            command = input("Enter a command (? to list):  ")
            for cmd in self.commands:
                if command.lower() == cmd.key:
                    print()
                    cmd.action()

    def quit(self):
        """Quit the game."""
        pr_blue("Goodbye.")
        self.running = False

    def list_commands(self):
        """List available commands in the current context."""
        pr_blue("Available commands:")
        for command in self.commands:
            print(f"{command.key} - {command.description}")

    def liftoff(self):
        """Move from the starport to orbit."""
        pr_blue(f"Lifting off to orbit {self.location.name}.")

        if self.ship.repair_status == RepairStatus.BROKEN:
            pr_red("Drive failure. Cannot lift off.")
            return

        # corner case - these messages assume passengers are coming
        # from the current world, which should be true most
        # of the time, but not necessarily all the time
        if self.ship.total_passenger_count > 0:
            print(f"Boarding {self.ship.total_passenger_count} passengers "
                  f"for {self.ship.destination.name}.")

        if self.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.ship.passengers if
                              p.passage == PassageClass.LOW]
            for passenger in low_passengers:
                passenger.guess_survivors(self.ship.low_passenger_count)

        self.location.liftoff()
        self.commands = orbit

    def _low_lottery(self):
        """Run the low passage lottery and apply results."""
        if self.ship.low_passenger_count > 0:
            low_passengers = [p for p in self.ship.passengers if
                                         p.passage == PassageClass.LOW]
            for passenger in low_passengers:
                if die_roll(2) + passenger.endurance + self.ship.medic_skill() < 5:
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
                self.financials.credit(low_lottery_amount)

    def land(self):
        """Move from orbit to the starport."""
        pr_blue(f"Landing on {self.location.name}.")
        if not self.ship.streamlined:
            print("Your ship is not streamlined and cannot land.")
            return

        if self.ship.repair_status == RepairStatus.BROKEN:
            pr_red("Drive failure. Cannot land.")
            return

        if self.ship.destination == self.location:
            if self.ship.total_passenger_count > 0:
                print(f"Passengers disembarking on {self.location.name}.")

                funds = Credits(sum(p.ticket_price.amount for p in self.ship.passengers))
                low_lottery_amount = Credits(10) * self.ship.low_passenger_count
                funds -= low_lottery_amount
                print(f"Receiving {funds} in passenger fares.")
                self.financials.credit(funds)

                self._low_lottery()

                self.ship.passengers = []
                self.ship.hold = [item for item in self.ship.hold
                                  if not isinstance(item, Baggage)]

        self.location.land()
        self.financials.berthing_fee(self.location.on_surface())
        self.commands = starport

    # TO_DO: almost identical to inbound_from_jump() - combine
    def outbound_to_jump(self):
        """Move from orbit to the jump point."""
        pr_blue(f"Travelling out to {self.location.name} jump point.")

        if self.ship.repair_status == RepairStatus.BROKEN:
            pr_red("Drive failure. Cannot travel to the jump point.")
            return

        tfc = self.ship.trip_fuel_cost
        if self.ship.current_fuel < tfc:
            print(f"Insufficient fuel. Travel to and from the jump point "
                  f"requires {tfc} tons, only "
                  f"{self.ship.current_fuel} tons in tanks.")
            return

        self.ship.current_fuel -= tfc // 2
        self.date.day += 1
        self.location.to_jump_point()
        self.commands = jump

    def inbound_from_jump(self):
        """Move from the jump point to orbit."""
        if isinstance(self.location, DeepSpace):
            pr_red("You are in deep space. There is no inner system to travel to.")
            return

        pr_blue(f"Travelling in to orbit {self.location.name}.")

        if self.ship.repair_status == RepairStatus.BROKEN:
            pr_red("Drive failure. Cannot travel to orbit.")
            return

        leg_fc = self.ship.trip_fuel_cost // 2
        if self.ship.current_fuel < leg_fc:
            print(f"Insufficient fuel. Travel in from the jump point "
                  f"requires {leg_fc} tons, only "
                  f"{self.ship.current_fuel} tons in tanks.")
            return

        self.ship.current_fuel -= leg_fc
        self.date.day += 1
        self.location.from_jump_point()
        self.commands = orbit

    # almost identical to leave_terminal(), consider merging
    def leave_depot(self):
        """Move from the trade depot to the starport."""
        pr_blue(f"Leaving {self.location.name} trade depot.")
        self.location.leave_trade()
        self.commands = starport

    def leave_terminal(self):
        """Move from the passenger terminal to the starport."""
        pr_blue(f"Leaving {self.location.name} passenger terminal.")
        self.location.leave_terminal()
        self.commands = starport

    def book_passengers(self):
        """Book passengers for travel to a destination."""
        pr_blue("Booking passengers.")

        jump_range = self.ship.jump_range
        potential_destinations = self.location.destinations.copy()

        if self.ship.destination is not None:
            if self.ship.destination == self.location:
                pr_red(f"There is still freight to be unloaded on {self.location.name}.")
                return
            if self.ship.destination in potential_destinations:
                print("You are under contract. Only showing passengers " +
                      f"for {self.ship.destination.name}:\n")
                destinations = [self.ship.destination]
            else:
                print(f"You are under contract to {self.ship.destination.name} " +
                      "but it is not within jump range of here.")
                return

        else:
            print(f"Available passenger destinations within jump-{jump_range}:\n")
            destinations = potential_destinations

        # for now we will stuff this in cargo depot, though it may better
        # be served by a separate class. If it _does_ stay in the depot, we
        # may want to adjust the nomenclature to make this more clear.
        coordinate, available = self.depot.get_available_passengers(destinations)
        if available is None:
            return

        destination = self.star_map.get_system_at_coordinate(coordinate)
        print(f"Passengers for {destination.name} (H,M,L): {available}")

        selection = (0,0,0)
        ship_capacity = (self.ship.empty_passenger_berths, self.ship.empty_low_berths)

        ship_hold = self.ship.free_space()
        while True:
            if available == (0,0,0):
                print(f"No more passengers available for {destination.name}.")
                break

            response = input("Choose a passenger by type (h, m, l, or q to exit): ")
            if response == 'q':
                break

            print(f"Remaining (H, M, L): {available}")
            print(f"Selected (H, M, L): {selection}")
            print(f"Empty ship berths (H+M, L): {ship_capacity}\n")

            if response == 'h':
                if available[PassageClass.HIGH.value] == 0:
                    print("No more high passengers available.")
                    continue
                if ship_capacity[0] == 0:
                    print("No more staterooms available.")
                    continue
                if ship_hold < 1:
                    print("No cargo space available for baggage.")
                    continue
                print("Adding a high passenger.")
                selection = tuple(a+b for a,b in zip(selection,(1,0,0)))
                available = tuple(a+b for a,b in zip(available,(-1,0,0)))
                ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-1,0)))
                ship_hold -= 1

            if response == 'm':
                if available[PassageClass.MIDDLE.value] == 0:
                    print("No more middle passengers available.")
                    continue
                if ship_capacity[0] == 0:
                    print("No more staterooms available.")
                    continue
                print("Adding a middle passenger.")
                selection = tuple(a+b for a,b in zip(selection,(0,1,0)))
                available = tuple(a+b for a,b in zip(available,(0,-1,0)))
                ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-1,0)))

            if response == 'l':
                if available[PassageClass.LOW.value] == 0:
                    print("No more low passengers available.")
                    continue
                if ship_capacity[1] == 0:
                    print("No more low berths available.")
                    continue
                print("Adding a low passenger.")
                selection = tuple(a+b for a,b in zip(selection,(0,0,1)))
                available = tuple(a+b for a,b in zip(available,(0,0,-1)))
                ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(0,-1)))

        print("Done selecting passengers.")

        if selection == (0,0,0):
            print("No passengers selected.")
            return
        print(f"Selected (H, M, L): {selection}")

        confirmation = confirm_input(f"Book {selection} passengers? (y/n)? ")
        if confirmation == 'n':
            print("Cancelling passenger selection.")
            return

        # TO_DO: need to consider the case where we already have passengers
        #        Probably want to wrap passenger field access in a property...
        high = [Passenger(PassageClass.HIGH, destination)
                for _ in range(selection[PassageClass.HIGH.value])]
        baggage = [Baggage(self.location, destination)
                   for _ in range(selection[PassageClass.HIGH.value])]
        middle = [Passenger(PassageClass.MIDDLE, destination)
                  for _ in range(selection[PassageClass.MIDDLE.value])]
        low = [Passenger(PassageClass.LOW, destination)
               for _ in range(selection[PassageClass.LOW.value])]

        self.ship.passengers += high
        self.ship.hold += baggage
        self.ship.passengers += middle
        self.ship.passengers += low
        self.depot.passengers[destination] = tuple(a-b for a,b in
                                                   zip(self.depot.passengers[destination],
                                                       selection))

    def to_depot(self):
        """Move from the starport to the trade depot."""
        pr_blue(f"Entering {self.location.name} trade depot.")
        self.location.join_trade()
        self.commands = trade

    def to_terminal(self):
        """Move from the starport to the passenger terminal."""
        pr_blue(f"Entering {self.location.name} passenger terminal.")
        self.location.enter_terminal()
        self.commands = passengers

    def jump(self):
        """Perform a jump to another StarSystem."""
        pr_blue("Preparing for jump.")

        if self.ship.repair_status in (RepairStatus.BROKEN, RepairStatus.PATCHED):
            pr_red("Drive failure. Cannot perform jump.")
            return

        if not self.ship.sufficient_jump_fuel():
            print(self.ship.insufficient_jump_fuel_message())
            return

        if not self.ship.sufficient_life_support():
            print(self.ship.insufficient_life_support_message())
            return

        jump_range = self.ship.jump_range
        print(f"Systems within jump-{jump_range}:")
        print_list(self.location.destinations)
        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(self.location.destinations):
            print("That is not a valid destination number.")
            return

        coordinate = self.location.destinations[destination_number].coordinate
        destination = self.star_map.get_system_at_coordinate(coordinate)

        if self.ship.destination is not None and self.ship.destination != destination:
            pr_red(f"Warning: your contracted destination is {self.ship.destination.name} " +
                   f"not {destination.name}.")

        confirmation = confirm_input(f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling jump.")
            return

        if (self.financials.maintenance_status(self.date.current_date)== "red" and
               die_roll(2) == 12):
            self.ship.repair_status = RepairStatus.BROKEN
            pr_red("Warning: drive failure! Unable to jump.")
            return

        if self.ship.fuel_quality == FuelQuality.UNREFINED:
            self.ship.unrefined_jump_counter += 1

        pr_red("Executing jump!")

        if self.ship.fuel_quality == FuelQuality.UNREFINED:
            modifier = 3
        else:
            modifier = -1
        if self.financials.maintenance_status(self.date.current_date) == "red":
            modifier += 2

        misjump_check = die_roll(2) + modifier
        if misjump_check > 11:
            pr_red("MISJUMP!")
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
            self.location = self.star_map.get_system_at_coordinate(misjump_target)
        else:
            self.location = destination

        self.location.detail = "jump"
        self.commands = jump

        if (self.ship.fuel_quality == FuelQuality.UNREFINED and
            die_roll(2) + self.ship.unrefined_jump_counter > 10):
            self.ship.repair_status = RepairStatus.BROKEN
            pr_red("Warning: drive failure!")

        coord = self.location.coordinate
        self.location.destinations = self.star_map.get_systems_within_range(coord,
                                                   jump_range)

        self.depot = CargoDepot(self.location, self.date.current_date)
        self.financials.location = destination

        self.ship.life_support_level = 0
        self.ship.current_fuel -= self.ship.jump_fuel_cost
        self.date.plus_week()

    def view_world(self):
        """View the characteristics of the local world."""
        pr_blue("Local world characteristics:")
        print(self.location)

    def refuel(self):
        """Refuel the Ship."""
        pr_blue("Refuelling ship.")
        if self.location.starport in ('E', 'X'):
            print(f"No fuel is available at starport {self.location.starport}.")
            return

        cost = self.ship.refuel(self.location.starport)
        self.financials.debit(cost)

    # TO_DO: should this be restricted at low-facility starports (E/X)?
    def recharge(self):
        """Recharge the Ship's life support system."""
        pr_blue("Replenishing life support system.")
        cost = self.ship.recharge()
        self.financials.debit(cost)

    def damage_control(self):
        """Partially repair damage to the Ship (Engineer)."""
        pr_blue("Ship's engineer repairing damage.")
        if self.ship.repair_status == RepairStatus.REPAIRED:
            print("Your ship is not damaged.")
            return
        if self.ship.repair_status == RepairStatus.PATCHED:
            print("Further repairs require starport facilities.")
            return
        self.date.day += 1
        if die_roll(2) + self.ship.engineering_skill() > 9:
            self.ship.repair_status = RepairStatus.PATCHED
            print("Ship partially repaired. Visit a starport for further work.")
        else:
            print("No progress today. Drives are still out of commission.")

    # TO_DO: the rules do not cover this procedure. No time or credits
    #        expenditure, etc. For now I'll just make this one week and free,
    #        but that probably ought to change.
    def repair_ship(self):
        """Fully repair damage to the Ship (Starport)."""
        pr_blue("Starport repairs.")
        if self.location.starport in ["D", "E", "X"]:
            print(f"No repair facilities available at starport {self.location.starport}")
            return
        if self.ship.repair_status == RepairStatus.REPAIRED:
            print("Your ship is not damaged.")
            return

        print("Your ship is fully repaired and decontaminated.")
        self.ship.repair_status = RepairStatus.REPAIRED
        self.ship.fuel_quality = FuelQuality.REFINED
        self.ship.unrefined_jump_counter = 0
        self.date.plus_week()

    def flush(self):
        """Decontaminate the Ship's fuel tanks."""
        pr_blue("Flushing out fuel tanks.")
        if self.ship.fuel_quality == FuelQuality.REFINED:
            print("Ship fuel tanks are clean. No need to flush.")
            return
        if self.location.starport in ('E', 'X'):
            print(f"There are no facilities to flush tanks at starport {self.location.starport}.")
            return

        print("Fuel tanks have been decontaminated.")
        self.ship.fuel_quality = FuelQuality.REFINED
        self.ship.unrefined_jump_counter = 0
        self.date.plus_week()

    def buy_cargo(self):
        """Purchase cargo for speculative trade."""
        pr_blue("Purchasing cargo.")
        print_list(self.depot.cargo)
        _, cargo = self.depot.get_cargo_lot(self.depot.cargo, "buy")
        if cargo is None:
            return

        quantity = self.depot.get_cargo_quantity("buy", cargo)
        if quantity is None:
            return

        if self.depot.insufficient_hold_space(cargo, quantity, self.ship.free_space()):
            return

        cost = self.depot.determine_price("purchase", cargo, quantity,
                                          None, self.ship.trade_skill())

        if self.depot.insufficient_funds(cost, self.financials.balance):
            return

        if not self.depot.confirm_transaction("purchase", cargo, quantity, cost):
            return

        self.depot.remove_cargo(self.depot.cargo, cargo, quantity)

        purchased = Cargo(cargo.name, quantity, cargo.price, cargo.unit_size,
                          cargo.purchase_dms, cargo.sale_dms, self.location)
        self.ship.load_cargo(purchased)

        self.financials.debit(cost)
        self.date.day += 1

    def sell_cargo(self):
        """Sell cargo in speculative trade."""
        pr_blue("Selling cargo.")
        cargoes = [c for c in self.ship.hold if isinstance(c, Cargo)]

        if len(cargoes) == 0:
            print("You have no cargo on board.")
            return

        print_list(cargoes)
        _, cargo = self.depot.get_cargo_lot(cargoes, "sell")
        if cargo is None:
            return

        if self.depot.invalid_cargo_origin(cargo):
            return

        broker_skill = self.depot.get_broker()

        quantity = self.depot.get_cargo_quantity("sell", cargo)
        if quantity is None:
            return

        sale_price = self.depot.determine_price("sale", cargo, quantity,
                                                broker_skill, self.ship.trade_skill())

        self.financials.debit(self.depot.broker_fee(broker_skill, sale_price))

        if not self.depot.confirm_transaction("sale", cargo, quantity, sale_price):
            return

        self.depot.remove_cargo(self.ship.hold, cargo, quantity)

        self.financials.credit(sale_price)
        self.date.day += 1

    def goods(self):
        """Show goods available for purchase."""
        pr_blue("Available cargo loads:")
        print_list(self.depot.cargo)

    def cargo_hold(self):
        """Show the contents of the Ship's cargo hold."""
        pr_blue("Contents of cargo hold:")
        contents = self.ship.cargo_hold()
        if len(contents) == 0:
            print("Empty.")
        else:
            print_list(contents)

    def passenger_manifest(self):
        """Show the Passenger's booked for transport."""
        pr_blue("Passenger manifest:")
        if self.ship.destination is None:
            destination = "None"
        else:
            destination = self.ship.destination.name
        print(f"High passengers: {self.ship.high_passenger_count}\n"
              f"Middle passengers: {self.ship.middle_passenger_count}\n"
              f"Low passengers: {self.ship.low_passenger_count}\n"
              f"DESTINATION: {destination}\n\n"
              f"Empty berths: {self.ship.empty_passenger_berths}\n"
              f"Empty low berths: {self.ship.empty_low_berths}")

    def crew_roster(self):
        """Show the Ship's crew."""
        pr_blue("Crew roster:")
        print_list(self.ship.crew)

    def wait_week(self):
        """Advance the Calendar by seven days."""
        pr_blue("Waiting.")
        self.date.plus_week()

    def view_ship(self):
        """View the details of the Ship."""
        pr_blue("Ship details:")
        print(self.ship)

    def view_map(self):
        """View all known StarSystems."""
        pr_blue("All known star systems:")
        systems = self.star_map.get_all_systems()
        print_list(systems)

    # Book 2 p. 35
    # Unrefined fuel may be obtained by skimming the atmosphere of a
    # gas giant if unavailable elsewhere. Most star systems have at
    # least one...
    #
    # Traveller '77 does not restrict this to streamlined ships, and
    # also does not include ocean refuelling, but I think I will be
    # including both options. (In all likelihood this will lean heavily
    # toward second edition...)
    def skim(self):
        """Refuel the Ship by skimming from a gas giant planet."""
        pr_blue("Skimming fuel from a gas giant planet.")
        if not self.location.gas_giant:
            # TO_DO: may want to tweak this message in deep space.
            print("There is no gas giant in this system. No fuel skimming possible.")
            return

        if not self.ship.streamlined:
            print("Your ship is not streamlined and cannot skim fuel.")
            return

        if self.ship.repair_status == RepairStatus.BROKEN:
            pr_red("Drive failure. Cannot skim fuel.")
            return

        if self.ship.current_fuel == self.ship.fuel_tank:
            print("Fuel tank is already full.")
            return

        self.ship.current_fuel = self.ship.fuel_tank
        self.ship.fuel_quality = FuelQuality.UNREFINED
        self.date.day += 1

    def maintenance(self):
        """Perform annual maintenance on the Ship."""
        pr_blue("Performing annual ship maintenance.")
        if self.location.starport not in ('A', 'B'):
            print("Annual maintenance can only be performed at class A or B starports.")
            return

        cost = self.ship.maintenance_cost()
        if self.financials.balance < cost:
            print("You do not have enough funds to pay for maintenance.\n"
                  f"It will cost {cost}. Your balance is {self.financials.balance}.")
            return

        # TO_DO: should we have a confirmation here?
        # TO_DO: should we warn or block if maintenance was performed recently?
        print(f"Performing maintenance. This will take two weeks. Charging {cost}.")
        self.financials.last_maintenance = self.date.current_date
        self.financials.debit(cost)
        self.date.day += 14    # should we wrap this in a method call?
        self.ship.repair_status = RepairStatus.REPAIRED

    def get_freight_destinations(self, potential_destinations, jump_range):
        result = []
        if self.ship.destination is not None:
            if self.ship.destination == self.location:
                pr_red(f"There is still freight to be unloaded on {self.location.name}.")
                return
            if self.ship.destination in potential_destinations:
                print("You are under contract. Only showing freight " +
                      f"for {self.ship.destination.name}:\n")
                result = [self.ship.destination]
            else:
                print(f"You are under contract to {self.ship.destination.name} " +
                      "but it is not within jump range of here.")
                return

        else:
            print(f"Available freight shipments within jump-{jump_range}:\n")
            result = potential_destinations

        return result

    def select_freight_lots(self, available):
        selection = []
        total_tonnage = 0
        hold_tonnage = self.ship.free_space()
        while True:
            if len(available) == 0:
                print(f"No more freight available for {destination.name}.")
                break

            response = input("Choose a shipment by tonnage ('q' to exit): ")
            if response == 'q':
                break

            try:
                response = int(response)
            except ValueError:
                print("Please input a number.")
                continue

            if response in available:
                if response <= hold_tonnage:
                    available.remove(response)
                    selection.append(response)
                    total_tonnage += response
                    hold_tonnage -= response
                    print(available)
                    print(f"Cargo space left: {hold_tonnage}")
                else:
                    pr_red("That shipment will not fit in your cargo hold.")
                    pr_red(f"Hold free space: {hold_tonnage}")
            else:
                pr_red(f"There are no shipments of size {response}.")

        print("Done selecting shipments.")
        return (total_tonnage, selection)

    # TO_DO: after getting this working, assess if any pieces should
    #        be pushed down
    def load_freight(self):
        """Select and load Freight onto the Ship."""
        pr_blue("Loading freight.")

        jump_range = self.ship.jump_range
        potential_destinations = self.location.destinations.copy()
        destinations = self.get_freight_destinations(potential_destinations, jump_range)

        coordinate, available = self.depot.get_available_freight(destinations)
        if available is None:
            return

        destination = self.star_map.get_system_at_coordinate(coordinate)
        print(f"Freight shipments for {destination.name}")
        print(available)

        total_tonnage, selection = self.select_freight_lots(available)

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

    def unload_freight(self):
        """Unload Freight from the Ship and receive payment."""
        pr_blue("Unloading freight.")

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
            pr_red("You are not at the contracted destination for this freight.")
            pr_red(f"It should be unloaded at {self.ship.destination.name}")

class Command:
    """Represents a command available to the player."""

    def __init__(self, key, description, action):
        """Create an instance of a Command."""
        self.key = key
        self.description = description
        self.action = action

game = Game()

always = [Command('q', 'Quit',
                  game.quit),
          Command('?', 'List commands',
                  game.list_commands),
          Command('c', 'Cargo hold contents',
                  game.cargo_hold),
          Command('v', 'View world characteristics',
                  game.view_world),
          Command('h', 'View ship details',
                  game.view_ship),
          Command('w', 'Wait a week',
                  game.wait_week),
          Command('d', 'Passenger manifest',
                  game.passenger_manifest),
          Command('e', 'Crew roster',
                  game.crew_roster),
          Command('k', 'Engineering damage control',
                  game.damage_control),
          Command('a', 'View star map',
                  game.view_map)]

starport = always + [Command('l', 'Lift off to orbit',
                             game.liftoff),
                     Command('t', 'Trade depot',
                             game.to_depot),
                     Command('f', 'Recharge life support',
                             game.recharge),
                     Command('m', 'Annual maintenance',
                             game.maintenance),
                     Command('p', 'Passenger terminal',
                             game.to_terminal),
                     Command('u', 'Flush fuel tanks',
                             game.flush),
                     Command('n', 'Repair ship',
                             game.repair_ship),
                     Command('r', 'Refuel',
                             game.refuel)]
starport = sorted(starport, key=lambda command: command.key)

orbit = always + [Command('g', 'Go to jump point',
                          game.outbound_to_jump),
                  Command('l', 'Land on surface',
                          game.land)]
orbit = sorted(orbit, key=lambda command: command.key)

jump = always + [Command('j', 'Jump to new system',
                         game.jump),
                 Command('s', 'Skim fuel from gas giant',
                         game.skim),
                 Command('i', 'Inbound to orbit',
                         game.inbound_from_jump)]
jump = sorted(jump, key=lambda command: command.key)

trade = always + [Command('l', 'Leave trade depot',
                          game.leave_depot),
                  Command('g', 'Show goods for sale',
                          game.goods),
                  Command('b', 'Buy cargo',
                          game.buy_cargo),
                  Command('s', 'Sell cargo',
                          game.sell_cargo),
                  Command('f', 'Load freight',
                          game.load_freight),
                  Command('u', 'Unload freight',
                          game.unload_freight)]
trade = sorted(trade, key=lambda command: command.key)

passengers = always + [Command('b', 'Book passengers',
                               game.book_passengers),
                       Command('l', 'Leave terminal',
                               game.leave_terminal)]
passengers = sorted(passengers, key=lambda command: command.key)

# keeping command characters straight...
# ALWAYS:   ? a ~ c d e ~ ~ h ~ ~ k ~ ~ ~ ~ q ~ ~ ~ ~ v w
# STARPORT:             f           l m n p   r   t u
# ORBIT:                  g         l
# JUMP:                       i j               s
# TRADE:        b       f g         l           s   u
# PASSENGERS:   b                   l

if __name__ == '__main__':
    game.run()
