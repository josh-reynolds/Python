from calendar import Calendar
from financials import Financials, Credits
from utilities import pr_yellow_on_red, int_input, confirm_input
from utilities import pr_blue, pr_red, print_list, die_roll, pr_green
from ship import Ship
from cargo import Cargo, CargoDepot, Freight, Passenger
from star_system import StarSystem
from star_map import StarMap, StarSystemFactory

class Game:
    def __init__(self):
        self.running = False
        self.date = Calendar()

        self.ship = Ship()
        self.ship.load_cargo(Cargo("Grain", 20, Credits(300), 1,
                                   {"Ag":-2,"Na":1,"In":2},
                                   {"Ag":-2}))

        self.star_map = StarMap({
            (0,0,0)  : StarSystemFactory.create("Yorbund", (0,0,0), "A", 8, 7, 5, 9, 5, 5, 10),
            (0,1,-1) : None,
            (0,-1,1) : StarSystemFactory.create("Mithril", (0,-1,1), "A", 8, 4, 0, 7, 5, 5, 10),
            (1,0,-1) : StarSystemFactory.create("Kinorb", (1,0,-1), "A", 8, 5, 5, 7, 5, 5, 10),
            (-1,0,1) : None,
            (1,-1,0) : None,
            (-1,1,0) : StarSystemFactory.create("Aramis", (-1,1,0), "A", 8, 6, 5, 8, 5, 5, 10)
            })

        self.location = self.star_map.get_system_at_coordinate((0,0,0))
        self.location.destinations = self.star_map.get_systems_within_range(self.location.coordinate,
                                                              self.ship.jump_range)
        self.financials = Financials(10000000, self.date.current_date, self.ship, self.location)
        self.depot = CargoDepot(self.location, self.date.current_date)

        self.date.add_observer(self.depot)
        self.date.add_observer(self.financials)

    def run(self):
        self.commands = orbit   # awkward, needs to change when location ctor detail changes
        self.running = True
        while self.running:
            pr_yellow_on_red(f"\n{self.date} : You are {self.location.description()}.")
            print(f"Credits: {self.financials.balance}"
                  f"\tFree hold space: {self.ship.free_space()} tons"
                  f"\tFuel: {self.ship.current_fuel}/{self.ship.fuel_tank} tons "
                  f"\tLife support: {self.ship.life_support_level}%")
            command = input("Enter a command (? to list):  ")
            for cmd in self.commands:
                if command.lower() == cmd.key:
                    print()
                    cmd.action()

    def quit(self):
        pr_blue("Goodbye.")
        self.running = False

    def list_commands(self):
        pr_blue("Available commands:")
        for command in self.commands:
            print(f"{command.key} - {command.description}")

    def liftoff(self):
        pr_blue(f"Lifting off to orbit {self.location.name}.")
        self.location.liftoff()
        self.commands = orbit

    def land(self):
        pr_blue(f"Landing on {self.location.name}.")
        if not self.ship.streamlined:
            print("Your ship is not streamlined and cannot land.")
            return

        self.location.land()
        self.financials.berthing_fee(self.location.on_surface())
        self.commands = starport

    # TO_DO: almost identical to inbound_from_jump() - combine
    def outbound_to_jump(self):
        pr_blue(f"Travelling out to {self.location.name} jump point.")
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
        pr_blue(f"Travelling in to orbit {self.location.name}.")
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
        pr_blue(f"Leaving {self.location.name} trade depot.")
        self.location.leave_trade()
        self.commands = starport

    def leave_terminal(self):
        pr_blue(f"Leaving {self.location.name} passenger terminal.")
        self.location.leave_terminal()
        self.commands = starport

    def book_passengers(self):
        pr_blue("Booking passengers.")

        jump_range = self.ship.jump_range
        potential_destinations = self.location.destinations.copy()

        # Work through order of operations... if passengers 
        # automatically disembark at landing, then they can't contribute
        # to a flag at ths point, just freight
        # But we don't care if there is freight if we're loading passengers
        # logic below lifted from load_freight() but will need adjustment
        # (and probably there as well to account for passengers)
        if self.ship.destination is not None:
            if self.ship.destination == self.location:
                pr_red(f"There is still freight to be unloaded on {self.location.name}.")
                return
            else:
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
        ship_capacity = (self.ship.passenger_berths, self.ship.low_berths)
        while True:
            if available == (0,0,0):
                print(f"No more passengers available for {destination.name}.")
                break

            response = input("Choose a passenger by type (h, m, l, or q to exit): ")
            if response == 'q':
                break

            print(f"Remaining (H, M, L): {available}")
            print(f"Selected (H, M, L): {selection}")
            print(f"Ship berths (H+M, L): {ship_capacity}\n") 

            if response == 'h':
                if available[Passenger.HIGH.value] == 0:
                    print("No more high passengers available.")
                    continue
                if ship_capacity[0] == 0:
                    print("No more staterooms available.")
                    continue
                print("Adding a high passenger.")
                selection = tuple(a+b for a,b in zip(selection,(1,0,0)))
                available = tuple(a+b for a,b in zip(available,(-1,0,0)))
                ship_capacity = tuple(a+b for a,b in zip(ship_capacity,(-1,0)))

            if response == 'm':
                if available[Passenger.MIDDLE.value] == 0:
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
                if available[Passenger.LOW.value] == 0:
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

        # confirm selection
        # add to ship
        #print(f"{total_tonnage} tons selected.")
#
        #confirmation = confirm_input(f"Load {total_tonnage} tons of freight? (y/n)? ")
        #if confirmation == 'n':
            #print("Cancelling freight selection.")
            #return
#
        #for entry in selection:
            #self.ship.load_cargo(Freight(entry,
                                         #self.location,
                                         #destination))
        #self.date.day += 1

    def to_depot(self):
        pr_blue(f"Entering {self.location.name} trade depot.")
        self.location.join_trade()
        self.commands = trade

    def to_terminal(self):
        pr_blue(f"Entering {self.location.name} passenger terminal.")
        self.location.enter_terminal()
        self.commands = passengers

    def jump(self):
        pr_blue("Preparing for jump.")
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

        pr_red("Executing jump!")
        self.location = destination
        self.location.detail = "jump"
        self.commands = jump

        self.location.destinations = self.star_map.get_systems_within_range(self.location.coordinate,
                                                   jump_range)

        self.depot = CargoDepot(self.location, self.date.current_date)
        self.financials.location = destination

        self.ship.life_support_level = 0
        self.ship.current_fuel -= self.ship.jump_fuel_cost
        self.date.plus_week()

    def view_world(self):
        pr_blue("Local world characteristics:")
        print(self.location)

    def refuel(self):
        pr_blue("Refuelling ship.")
        if self.location.starport in ('E', 'X'):
            print(f"No fuel is available at starport {self.location.starport}.")
            return

        cost = self.ship.refuel()
        self.financials.debit(cost)

    def recharge(self):
        pr_blue("Replenishing life support system.")
        cost = self.ship.recharge()
        self.financials.debit(cost)

    def buy_cargo(self):
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
        pr_blue("Available cargo loads:")
        print_list(self.depot.cargo)

    def cargo_hold(self):
        pr_blue("Contents of cargo hold:")
        print_list(self.ship.cargo_hold())

    def wait_week(self):
        pr_blue("Waiting.")
        self.date.plus_week()

    def view_ship(self):
        pr_blue("Ship details:")
        print(self.ship)

    def view_map(self):
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
        pr_blue("Skimming fuel from a gas giant planet.")
        if not self.location.gas_giant:
            print("There is no gas giant in this system. No fuel skimming possible.")
            return

        if not self.ship.streamlined:
            print("Your ship is not streamlined and cannot skim fuel.")
            return

        if self.ship.current_fuel == self.ship.fuel_tank:
            print("Fuel tank is already full.")
            return

        # will need to mark this as unrefined fuel when we implement that
        self.ship.current_fuel = self.ship.fuel_tank
        self.date.day += 1

    def maintenance(self):
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

    # TO_DO: after getting this working, assess if any pieces should
    #        be pushed down
    # If passengers have been picked already, only show that destination
    def load_freight(self):
        pr_blue("Loading freight.")

        jump_range = self.ship.jump_range
        potential_destinations = self.location.destinations.copy()

        if self.ship.destination is not None:
            if self.ship.destination == self.location:
                pr_red(f"There is still freight to be unloaded on {self.location.name}.")
                return
            else:
                if self.ship.destination in potential_destinations:
                    print("You are under contract. Only showing freight " +
                          f"for {self.ship.destination.name}:\n")
                    destinations = [self.ship.destination]
                else:
                    print(f"You are under contract to {self.ship.destination.name} " +
                          "but it is not within jump range of here.")
                    return

        else:
            print(f"Available freight shipments within jump-{jump_range}:\n")
            destinations = potential_destinations

        coordinate, available = self.depot.get_available_freight(destinations)
        if available is None:
            return

        destination = self.star_map.get_system_at_coordinate(coordinate)
        print(f"Freight shipments for {destination.name}")
        print(available)

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
                if response < hold_tonnage:
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

        if total_tonnage == 0:
            print("No freight shipments selected.")
            return
        print(f"{total_tonnage} tons selected.")

        confirmation = confirm_input(f"Load {total_tonnage} tons of freight? (y/n)? ")
        if confirmation == 'n':
            print("Cancelling freight selection.")
            return

        for entry in selection:
            self.ship.load_cargo(Freight(entry,
                                         self.location,
                                         destination))
        self.date.day += 1

    def unload_freight(self):
        pr_blue("Unloading freight.")

        # truth table: passengers, freight, destination flag,...

        # It should not be possible for there to be freight in the hold,
        # and a destination flag set to None. Should we assert just
        # in case, so we could track down any such bug:
        if self.ship.destination is None:
            print(f"You have no contracted destination.")
            return

        freight = [f for f in self.ship.hold if isinstance(f, Freight)]
        if len(freight) == 0:
            print(f"You have no freight on board.")
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
    def __init__(self, key, description, action):
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

if __name__ == '__main__':
    game.run()
