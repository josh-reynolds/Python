"""Contains classes to represent Traveller star map hexes.

Hex - base class for map hexes.
DeepSpace - represents an empty map hex.
StarSystem - represents a map hex containing a star system.
"""

class Hex:
    """Base class for map hexes."""

    def __init__(self, coordinate):
        self.coordinate = coordinate

class DeepSpace(Hex):
    """Represents an empty map hex."""

    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.detail = ""
        self.destinations = []
        self.population = 0
        self.gas_giant = False

    def description(self):
        return "stranded in deep space"

    def __repr__(self):
        return f"{self.coordinate} - Deep Space"

class StarSystem(Hex):
    """Represents a map hex containing a star system."""

    def __init__(self, name, coordinate, starport, size, atmosphere,
                 hydrographics, population, government, law, tech, gas_giant=True):
        super().__init__(coordinate)
        self.name = name
        self.starport = starport
        self.size = size
        self.atmosphere = atmosphere
        self.hydrographics = hydrographics
        self.population = population
        self.government = government
        self.law = law
        self.tech = tech
        self.gas_giant = gas_giant
        self.detail = "orbit"
        self.destinations = []

        self.agricultural = False
        if (atmosphere in (4, 5, 6, 7, 8, 9) and
            hydrographics in (4, 5, 6, 7, 8) and
            population in (5, 6, 7)):
            self.agricultural = True

        self.nonagricultural = False
        if (atmosphere in (0, 1, 2, 3) and
            hydrographics in (0, 1, 2, 3) and
            population in (6, 7, 8, 9, 10)):
            self.nonagricultural = True

        self.industrial = False
        if (atmosphere in (0, 1, 2, 4, 7, 9) and
            population in (9, 10)):
            self.industrial = True

        self.nonindustrial = False
        if population in (0, 1, 2, 3, 4, 5, 6):
            self.nonindustrial = True

        self.rich = False
        if (government in (4, 5, 6, 7, 8, 9) and
            atmosphere in (6, 8) and
            population in (6, 7, 8)):
            self.rich = True

        self.poor = False
        if (atmosphere in (2, 3, 4, 5) and
            hydrographics in (0, 1, 2, 3)):
            self.poor = True

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.coordinate == other.coordinate
        return NotImplemented

    def __hash__(self):
        return hash((self.coordinate, self.name))

    # TO_DO: we will need to handle digits > 9. Traveller uses 'extended hex'
    # for now we can probably get away with simple f-string conversion:
    #    f"{value:X}"
    # Check if '77 can generate any values above 15 (F). It's certainly
    # possible in later editions, not sure here...
    # If so, a simple method that indexes a string would work.
    #    chars = "01234567890ABCDEFGHJKLMNPQRSTUVWXYZ"    # omit 'I' and 'O'
    #    e_hex = chars[value]
    def __repr__(self):
        url = f"{self.starport}{self.size:X}{self.atmosphere:X}" +\
              f"{self.hydrographics:X}{self.population:X}{self.government:X}" +\
              f"{self.law:X}-{self.tech:X}"
        if self.agricultural:
            url += " Ag"
        if self.nonagricultural:
            url += " Na"
        if self.industrial:
            url += " In"
        if self.nonindustrial:
            url += " Ni"
        if self.rich:
            url += " Ri"
        if self.poor:
            url += " Po"
        if self.gas_giant:
            url += " - G"
        return f"{self.coordinate} - {self.name} - {url}"

    def description(self):
        if self.detail == "starport":
            return f"at the {self.name} starport"

        if self.detail == "orbit":
            return f"in orbit around {self.name}"

        if self.detail == "jump":
            return f"at the {self.name} jump point"

        if self.detail == "trade":
            return f"at the {self.name} trade depot"

        if self.detail == "terminal":
            return f"at the {self.name} passenger terminal"

        return "ERROR"    # should not be able to reach this point
                          # ensure there are only five (currently)
                          # possible values for self.detail?

    def on_surface(self):
        return self.detail in ('starport', 'trade', 'terminal')

    def land(self):
        if self.detail == "orbit":
            self.detail = "starport"

    def liftoff(self):
        if self.detail == "starport":
            self.detail = "orbit"

    def to_jump_point(self):
        if self.detail == "orbit":
            self.detail = "jump"

    def from_jump_point(self):
        if self.detail == "jump":
            self.detail = "orbit"

    def join_trade(self):
        if self.detail == "starport":
            self.detail = "trade"

    def leave_trade(self):
        if self.detail == "trade":
            self.detail = "starport"

    def enter_terminal(self):
        if self.detail == "starport":
            self.detail = "terminal"

    def leave_terminal(self):
        if self.detail == "terminal":
            self.detail = "starport"
