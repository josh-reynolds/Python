from calendar import Calendar
from financials import Financials, Credits
from utilities import pr_yellow_on_red, int_input, confirm_input
from utilities import pr_blue, pr_red, print_list, die_roll, pr_green
from ship import Ship
from cargo import Cargo, CargoDepot, Freight
from star_system import StarSystem
from star_map import StarMap

class Game:
    def __init__(self):
        self.running = False
        self.date = Calendar()

        self.ship = Ship()
        self.ship.load_cargo(Cargo("Grain", 20, Credits(300), 1,
                                   {"Ag":-2,"Na":1,"In":2},
                                   {"Ag":-2}))

        self.star_map = StarMap({
            (0,0,0)  : StarSystem("Yorbund", (0,0,0), "A", 8, 7, 5, 9, 5, 5, 10),
            (0,1,-1) : None,
            (0,-1,1) : StarSystem("Mithril", (0,-1,1), "A", 8, 4, 0, 7, 5, 5, 10),
            (1,0,-1) : StarSystem("Kinorb", (1,0,-1), "A", 8, 5, 5, 7, 5, 5, 10),
            (-1,0,1) : None,
            (1,-1,0) : None,
            (-1,1,0) : StarSystem("Aramis", (-1,1,0), "A", 8, 6, 5, 8, 5, 5, 10)
            })

        self.location = self.star_map.get_system_at_coordinate((0,0,0))
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
        self.commands = grounded

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

    def leave(self):
        pr_blue(f"Leaving {self.location.name} trade depot.")
        self.location.leave_trade()
        self.commands = grounded

    def to_trade(self):
        pr_blue(f"Entering {self.location.name} trade depot.")
        self.location.join_trade()
        self.commands = trade

    def jump(self):
        pr_blue("Preparing for jump.")
        jump_fuel = self.ship.jump_fuel_cost
        if jump_fuel > self.ship.current_fuel:
            print(f"Insufficient fuel. Jump requires {jump_fuel} tons, only "
                  f"{self.ship.current_fuel} tons in tanks.")
            return

        life_support = self.ship.life_support_level
        if life_support < 100:
            print(f"Insufficient life support to survive jump.\n"
                  f"Life support is at {life_support}%.")
            return

        # TO_DO: warning if selected destination does not match Ship.destination
        jump_range = self.ship.jump_range
        destinations = self.star_map.get_systems_within_range(self.location.coordinate,
                                                              jump_range)
        print(f"Systems within jump-{jump_range}:")
        print_list(destinations)
        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(destinations):
            print("That is not a valid destination number.")
            return
        coordinate = destinations[destination_number].coordinate
        destination = self.star_map.get_system_at_coordinate(coordinate)

        if self.ship.destination is not None and self.ship.destination != destination:
            pr_red(f"Your contracted destination is {self.ship.destination.name} " + 
                   f"not {destination.name}.")

        confirmation = confirm_input(f"Confirming jump to {destination.name} (y/n)? ")
        if confirmation == 'n':
            print("Cancelling jump.")
            return

        pr_red("Executing jump!")
        self.location = destination
        self.location.detail = "jump"
        self.commands = jump

        # TO_DO: calling for side effect of generating
        #        neighboring systems... refactor this
        _ = self.star_map.get_systems_within_range(self.location.coordinate,
                                                   jump_range)

        self.depot.system = destination
        self.depot.cargo = self.depot.determine_cargo()
        self.financials.location = destination

        self.ship.life_support_level = 0
        self.ship.current_fuel -= jump_fuel
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
        print_list(self.ship.hold)
        _, cargo = self.depot.get_cargo_lot(self.ship.hold, "sell")
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
    # Freight list needs to persist between invocations, and
    #   be refreshed weekly like cargo
    # If passengers have been picked already, only show that destination
    # Automatically exit selection loop if no remaining cargoes will fit?
    # Ability to put shipments back?
    def load_freight(self):
        pr_blue("Loading freight.")

        # this is lifted almost verbatim from jump() - refactor
        jump_range = self.ship.jump_range
        if self.ship.destination is not None:
            destinations = [self.ship.destination]
        else:
            destinations = self.star_map.get_systems_within_range(
                    self.location.coordinate,
                    jump_range)

        print(f"Available freight shipments within jump-{jump_range}:\n")

        freight_shipments = []
        for world in destinations:
            shipments = []
            for i in range(world.population):
                shipments.append(die_roll() * 5)
            shipments = sorted(shipments)
            freight_shipments.append(shipments)

        for i,world in enumerate(destinations):
            pr_green(f"{i} - {world}")
            print("   ", freight_shipments[i])
            print()

        destination_number = int_input("Enter destination number: ")
        if destination_number >= len(destinations):
            print("That is not a valid destination number.")
            return
        coordinate = destinations[destination_number].coordinate
        destination = self.star_map.get_system_at_coordinate(coordinate)

        available = freight_shipments[destination_number]
        print(f"Freight shipments for {destination.name}")
        print(available)

        selection = []
        total_tonnage = 0
        hold_tonnage = self.ship.free_space()
        while True:
            if len(available) == 0:
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
        print(f"{total_tonnage} tons selected.")

        # Corner case: 0 tons selected
        confirmation = confirm_input(f"Load {total_tonnage} tons of freight? (y/n)? ")
        if confirmation == 'n':
            print("Cancelling freight selection.")
            return

        for entry in selection:
            self.ship.load_cargo(Freight(entry,
                                         self.location,
                                         destination))
        self.ship.destination = destination
        self.date.day += 1

    def unload_freight(self):
        pr_blue("Unloading freight.")

        # corner case: no freight is on board
        # corner case: freight for a different destination is on board

        if self.ship.destination == self.location:
            freight_tonnage = sum([f.tonnage for f in self.ship.hold if isinstance(f, Freight)])
            self.ship.hold = [c for c in self.ship.hold if isinstance(c, Cargo)]

            payment = Credits(1000 * freight_tonnage)
            self.financials.credit(Credits(1000 * freight_tonnage))
            print(f"Receiving payment of {payment} for {freight_tonnage} tons shipped.")

            self.date.day += 1

            self.ship.destination = None   # TO_DO: adjust once we have passengers

        else:
            # corner case: freight for multiple destinations is on board
            pr_red("You are not at the contracted destination for this freight!")
            pr_red(f"This should be unloaded at {self.ship.destination}")

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
          Command('p', 'View ship details',
                  game.view_ship),
          Command('w', 'Wait a week',
                  game.wait_week),
          Command('a', 'View star map',
                  game.view_map)]

grounded = always + [Command('l', 'Lift off to orbit',
                             game.liftoff),
                     Command('t', 'Trade',
                             game.to_trade),
                     Command('f', 'Recharge life support',
                             game.recharge),
                     Command('m', 'Annual maintenance',
                             game.maintenance),
                     Command('r', 'Refuel',
                             game.refuel)]
grounded = sorted(grounded, key=lambda command: command.key)

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

trade = always + [Command('l', 'Leave trade interaction',
                          game.leave),
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

if __name__ == '__main__':
    game.run()
