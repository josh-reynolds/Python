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
        self.depot = CargoDepot(self.location, self.ship, self.financials, self.date.current_date)

        self.ship.load_cargo(Cargo("Grain", 20, Credits(300), 1,
                                   {"Ag":-2,"Na":1,"In":2}, 
                                   {"Ag":-2}))

        # BUG: this will break when we jump to a new system, fix!
        self.date.add_observer(self.depot)
        self.date.add_observer(self.financials)

    def run(self):
        self.commands = grounded
        self.running = True
        while self.running:
            pr_yellow_on_red(f"\n{self.date} : You are {self.location.description()}.")
            print(f"Credits: {self.financials.balance}"
                  f"\tFree hold space: {self.ship.free_space()} tons"
                  f"\tFuel: {self.ship.current_fuel}/{self.ship.fuel_tank} tons")
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
            print(f"Insufficient fuel. Jump costs {jfc} tons, only "
                  f"{self.ship.current_fuel} tons in tanks.")
            return
        j_range = self.ship.jump_range

    def view_world(self):
        print(self.location)

    def refuel(self):
        cost = self.ship.refuel()
        self.financials.debit(cost)

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
                  game.ship.cargo_hold,
                  'Contents of cargo hold:'),
          Command('v', 'View world characteristics',
                  game.view_world,
                  'Local world characteristics:'),
          Command('w', 'Wait a week',
                  game.date.plus_week,
                  'Waiting')]

grounded = always + [Command('l', 'Lift off to orbit', 
                             game.liftoff,
                             'Lifting off to orbit.'),
                     Command('t', 'Trade',
                             game.to_trade,
                             'Trading goods.'),
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
                         'Executing jump sequence!'),
                 Command('i', 'Inbound to orbit',
                         game.inbound_from_jump,
                         f"Travel in to orbit {game.location.name}")]
jump = sorted(jump, key=lambda command: command.key)

trade = always + [Command('l', 'Leave trade interaction',
                          game.leave,
                          'Leaving trader depot.'),
                  Command('g', 'Show goods for sale',
                          game.depot.goods,
                          'Available cargo loads:'),
                  Command('b', 'Buy cargo',
                          game.depot.buy_cargo,
                          'Purchasing cargo'),
                  Command('s', 'Sell cargo',
                          game.depot.sell_cargo,
                          'Selling cargo')]
trade = sorted(trade, key=lambda command: command.key)

if __name__ == '__main__':
    game.run()
