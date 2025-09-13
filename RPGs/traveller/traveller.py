from financials import Financials, Credits
from utilities import pr_yellow_on_red
from calendar import Calendar
from ship import Ship
from cargo import Cargo, CargoDepot
from star_system import StarSystem

class Game:
    def __init__(self):
        self.running = False
        self.date = Calendar()
        self.ship = Ship()
        self.location = StarSystem("Yorbund", "A", 5, 5, 5, 5) 
        self.financials = Financials(10000000, self.date.current_date, self.ship, self.location)
        self.depot = CargoDepot(self.location, self.date.current_date)

        self.ship.load_cargo(Cargo("Grain", 20, Credits(300), 1,
                                   {"Ag":-2,"Na":1,"In":2}, 
                                   {"Ag":-2}))

        # BUG: this will break when we jump to a new system, fix!
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
            for c in self.commands:
                if command.lower() == c.key:
                    print(c.message)
                    c.action()

    def quit(self):
        self.running = False

    def list_commands(self):
        for c in self.commands:
            print(f"{c.key} - {c.description}")

    def liftoff(self):
        self.location.liftoff()
        self.commands = orbit

    def land(self):
        if not self.ship.streamlined:
            print("Your ship is not streamlined and cannot land.")
            return

        self.location.land()
        self.financials.berthing_fee(self.location.on_surface())
        self.commands = grounded

    def outbound_to_jump(self):
        self.location.to_jump_point()
        self.commands = jump

    def inbound_from_jump(self):
        self.location.from_jump_point()
        self.commands = orbit

    def leave(self):
        self.location.leave_trade()
        self.commands = grounded

    def to_trade(self):
        self.location.join_trade()
        self.commands = trade

    def jump(self):
        jfc = self.ship.jump_fuel_cost
        if jfc > self.ship.current_fuel:
            print(f"Insufficient fuel. Jump requires {jfc} tons, only "
                  f"{self.ship.current_fuel} tons in tanks.")
            return

        ls = self.ship.life_support_level
        if ls < 100:
            print(f"Insufficient life support to survive jump.\n"
                  f"Life support is at {ls}%.")
            return

        j_range = self.ship.jump_range

    def view_world(self):
        print(self.location)

    def refuel(self):
        cost = self.ship.refuel()
        self.financials.debit(cost)

    def recharge(self):
        cost = self.ship.recharge()
        self.financials.debit(cost)
        
    def buy_cargo(self):
        item_number, cargo = self.depot.get_cargo_lot(self.depot.cargo, "buy")
        if cargo == None:
            return

        quantity = self.depot.get_cargo_quantity("buy", cargo)
        if quantity == None:
            return
        
        if self.depot.insufficient_hold_space(cargo, quantity, self.ship.free_space()):
            return

        cost = self.depot.determine_price("purchase", cargo, quantity, item_number, 
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

    def sell_cargo(self):
        item_number, cargo = self.depot.get_cargo_lot(self.ship.hold, "sell")
        if cargo == None:
            return

        if self.depot.invalid_cargo_origin(cargo):
            return

        broker_skill = self.depot.get_broker()

        quantity = self.depot.get_cargo_quantity("sell", cargo)
        if quantity == None:
            return

        sale_price = self.depot.determine_price("sale", cargo, quantity, item_number, 
                                                broker_skill, self.ship.trade_skill())

        self.financials.debit(self.depot.broker_fee(broker_skill, sale_price))

        if not self.depot.confirm_transaction("sale", cargo, quantity, sale_price):
            return

        self.depot.remove_cargo(self.ship.hold, cargo, quantity)

        self.financials.credit(sale_price)

    def goods(self):
        self.depot.goods()

    def cargo_hold(self):
        self.ship.cargo_hold()

    def wait_week(self):
        self.date.plus_week()

    def view_ship(self):
        print(self.ship)

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

class Command:
    def __init__(self, key, description, action, message):
        self.key = key
        self.description = description
        self.action = action
        self.message = message

game = Game()

always = [Command('q', 'Quit',
                  game.quit,
                  'Goodbye.'),
          Command('?', 'List commands',
                  game.list_commands,
                  'Available commands:'),
          Command('c', 'Cargo hold contents',
                  game.cargo_hold,
                  'Contents of cargo hold:'),
          Command('v', 'View world characteristics',
                  game.view_world,
                  'Local world characteristics:'),
          Command('p', 'View ship details',
                  game.view_ship,
                  'Ship details:'),
          Command('w', 'Wait a week',
                  game.wait_week,
                  'Waiting')]

grounded = always + [Command('l', 'Lift off to orbit', 
                             game.liftoff,
                             'Lifting off to orbit.'),
                     Command('t', 'Trade',
                             game.to_trade,
                             'Trading goods.'),
                     Command('f', 'Recharge life support',
                             game.recharge,
                             'Replenishing life support system.'),
                     Command('r', 'Refuel',
                             game.refuel,
                             'Refuelling ship.')]
grounded = sorted(grounded, key=lambda command: command.key)

orbit = always + [Command('g', 'Go to jump point',
                          game.outbound_to_jump,
                          'Travelling to jump point.'),
                  Command('l', 'Land on surface',
                          game.land,
                          f"Landing on {game.location.name}")]
orbit = sorted(orbit, key=lambda command: command.key)

jump = always + [Command('j', 'Jump to new system',
                         game.jump,
                         'Preparing for jump.'),
                 Command('s', 'Skim fuel from gas giant',
                         game.skim,
                         'Skimming fuel from a gas giant planet.'),
                 Command('i', 'Inbound to orbit',
                         game.inbound_from_jump,
                         f"Travel in to orbit {game.location.name}")]
jump = sorted(jump, key=lambda command: command.key)

trade = always + [Command('l', 'Leave trade interaction',
                          game.leave,
                          'Leaving trader depot.'),
                  Command('g', 'Show goods for sale',
                          game.goods,
                          'Available cargo loads:'),
                  Command('b', 'Buy cargo',
                          game.buy_cargo,
                          'Purchasing cargo'),
                  Command('s', 'Sell cargo',
                          game.sell_cargo,
                          'Selling cargo')]
trade = sorted(trade, key=lambda command: command.key)

if __name__ == '__main__':
    game.run()
