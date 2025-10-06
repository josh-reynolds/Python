"""Contains classes to represent Traveller star map hexes.

Hex - base class for map hexes.
DeepSpace - represents an empty map hex.
StarSystem - represents a map hex containing a star system.
"""

class Hex:
    """Base class for map hexes."""

    def __init__(self, coordinate):
        """Create an instance of a Hex."""
        self.coordinate = coordinate

class DeepSpace(Hex):
    """Represents an empty map hex."""

    def __init__(self, coordinate):
        """Create an instance of a DeepSpace object."""
        super().__init__(coordinate)
        self.detail = ""
        self.destinations = []
        self.population = 0
        self.gas_giant = False

    def description(self):
        """Return the descriptor for a DeepSpace hex."""
        return "stranded in deep space"

    def __repr__(self):
        """Return the string representation of a DeepSpace object."""
        return f"{self.coordinate} - Deep Space"

class UWP:
    """Represents a Traveller Universal World Profile."""

    def __init__(self, starport, size, atmosphere, hydrographics,
                 population, government, law, tech):
        """Create an instance of a UWP object."""
        self.starport = starport
        self.size = size
        self.atmosphere = atmosphere
        self.hydrographics = hydrographics
        self.population = population
        self.government = government
        self.law = law
        self.tech = tech

class StarSystem(Hex):
    """Represents a map hex containing a star system."""

    def __init__(self, name, coordinate, uwp, gas_giant=True):
        """Create an instance of a StarSystem."""
        super().__init__(coordinate)
        self.name = name
        self.uwp = uwp
        self.gas_giant = gas_giant
        self.detail = "orbit"
        self.destinations = []

        self.agricultural = False
        if (self.atmosphere in (4, 5, 6, 7, 8, 9) and
            self.hydrographics in (4, 5, 6, 7, 8) and
            self.population in (5, 6, 7)):
            self.agricultural = True

        self.nonagricultural = False
        if (self.atmosphere in (0, 1, 2, 3) and
            self.hydrographics in (0, 1, 2, 3) and
            self.population in (6, 7, 8, 9, 10)):
            self.nonagricultural = True

        self.industrial = False
        if (self.atmosphere in (0, 1, 2, 4, 7, 9) and
            self.population in (9, 10)):
            self.industrial = True

        self.nonindustrial = False
        if self.population in (0, 1, 2, 3, 4, 5, 6):
            self.nonindustrial = True

        self.rich = False
        if (self.government in (4, 5, 6, 7, 8, 9) and
            self.atmosphere in (6, 8) and
            self.population in (6, 7, 8)):
            self.rich = True

        self.poor = False
        if (self.atmosphere in (2, 3, 4, 5) and
            self.hydrographics in (0, 1, 2, 3)):
            self.poor = True

    def __eq__(self, other):
        """Test whether two StarSystem objects are equal."""
        if type(other) is type(self):
            return self.name == other.name and self.coordinate == other.coordinate
        return NotImplemented

    def __hash__(self):
        """Calculate the hash value for a StarSystem object."""
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
        """Return the string representation of a StarSystem object."""
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

    @property
    def starport(self):
        """Return the UWP starport value."""
        return self.uwp.starport

    @property
    def size(self):
        """Return the UWP size value."""
        return self.uwp.size

    @property
    def atmosphere(self):
        """Return the UWP atmosphere value."""
        return self.uwp.atmosphere

    @property
    def hydrographics(self):
        """Return the UWP hydrographics value."""
        return self.uwp.hydrographics

    @property
    def population(self):
        """Return the UWP population value."""
        return self.uwp.population

    @property
    def government(self):
        """Return the UWP government value."""
        return self.uwp.government

    @property
    def law(self):
        """Return the UWP law level value."""
        return self.uwp.law

    @property
    def tech(self):
        """Return the UWP tech level value."""
        return self.uwp.tech

    def description(self):
        """Return the descriptor for the current location within the StarSystem."""
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
        """Test whether the player is currently on the world's surface."""
        return self.detail in ('starport', 'trade', 'terminal')

    def land(self):
        """Move from orbit to the starport."""
        if self.detail == "orbit":
            self.detail = "starport"

    def liftoff(self):
        """Move from the starport to orbit."""
        if self.detail == "starport":
            self.detail = "orbit"

    def to_jump_point(self):
        """Move from orbit to the jump point."""
        if self.detail == "orbit":
            self.detail = "jump"

    def from_jump_point(self):
        """Move from the jump point to orbit."""
        if self.detail == "jump":
            self.detail = "orbit"

    def join_trade(self):
        """Move from the starport to the trade depot."""
        if self.detail == "starport":
            self.detail = "trade"

    def leave_trade(self):
        """Move from the trade depot to the starport."""
        if self.detail == "trade":
            self.detail = "starport"

    def enter_terminal(self):
        """Move from the starport to the passenger terminal."""
        if self.detail == "starport":
            self.detail = "terminal"

    def leave_terminal(self):
        """Move from the passenger terminal to the starport."""
        if self.detail == "terminal":
            self.detail = "starport"
