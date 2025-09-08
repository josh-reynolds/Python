from cargo import CargoDepot

class StarSystem:
    def __init__(self, name, atmosphere, hydrographics, population, government, current_date, ship, financials):
        self.name = name
        self.atmosphere = atmosphere
        self.hydrographics = hydrographics
        self.population = population
        self.government = government
        self.detail = "surface"
        self.depot = CargoDepot(self, ship, financials, current_date)

        self.agricultural = False
        if (atmosphere >= 4 and atmosphere <= 9 and 
            hydrographics >= 4 and hydrographics <= 8 and
            population >= 5 and population <= 7):
            self.agricultural = True

        self.nonagricultural = False
        if (atmosphere <= 3 and 
            hydrographics <= 3 and
            population >= 6):
            self.nonagricultural = True

        self.industrial = False
        if ((atmosphere <= 2 or atmosphere == 4 or atmosphere == 7 or atmosphere == 9) and
            population >= 9):
            self.industrial = True

        self.nonindustrial = False
        if population <= 6:
            self.nonindustrial = True

        self.rich = False
        if (government >= 4 and government <= 9 and
            (atmosphere == 6 or atmosphere == 8) and
            population >= 6 and population <= 8):
            self.rich = True

        self.poor = False
        if (atmosphere >= 2 and atmosphere <= 5 and
            hydrographics <= 3):
            self.poor = True

    #   making a big assumption that worlds cannot share the
    #   same name - good enough for now
    def __eq__(self, other):
        if isinstance(other, StarSystem):
            return self.name == other.name
        return False

    def __repr__(self):
        url = f"{self.atmosphere}{self.hydrographics}{self.population}{self.government}"
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
        return f"{self.name} - {url}"

    def description(self):
        if self.detail == "surface":
            return f"on {self.name}"
        elif self.detail == "orbit":
            return f"in orbit around {self.name}"
        elif self.detail == "jump":
            return f"at the {self.name} jump point"
        elif self.detail == "trade":
            return f"at the {self.name} trade depot"

    def on_surface(self):
        return self.detail == "surface" or self.detail == "trade"

    def land(self):
        if self.detail == "orbit":
            self.detail = "surface"

    def liftoff(self):
        if self.detail == "surface":
            self.detail = "orbit"

    def to_jump_point(self):
        if self.detail == "orbit":
            self.detail = "jump"

    def from_jump_point(self):
        if self.detail == "jump":
            self.detail = "orbit"

    def join_trade(self):
        if self.detail == "surface":
            self.detail = "trade"

    def leave_trade(self):
        if self.detail == "trade":
            self.detail = "surface"
