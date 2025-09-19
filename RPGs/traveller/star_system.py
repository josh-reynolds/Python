import unittest
from cargo import CargoDepot

class StarSystem:
    def __init__(self, name, starport, atmosphere, hydrographics, 
                 population, government, gas_giant=True):
        self.name = name
        self.coordinate = 111
        self.starport = starport
        self.atmosphere = atmosphere
        self.hydrographics = hydrographics
        self.population = population
        self.government = government
        self.gas_giant = gas_giant
        self.detail = "orbit"

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

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.coordinate == other.coordinate
        return NotImplemented

    def __repr__(self):
        url = f"{self.starport}{self.atmosphere}{self.hydrographics}{self.population}{self.government}"
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

class StarSystemTestCase(unittest.TestCase):
    def setUp(self):
        StarSystemTestCase.system = StarSystem("Test", "A", 9, 9, 9, 9, True)

    def test_landing(self):
        world = StarSystemTestCase.system
        self.assertEqual(world.detail, "orbit")
        world.land()
        self.assertEqual(world.detail, "surface")
        world.land()
        self.assertEqual(world.detail, "surface")

    def test_liftoff(self):
        world = StarSystemTestCase.system
        world.detail = "surface"
        world.liftoff()
        self.assertEqual(world.detail, "orbit")
        world.liftoff()
        self.assertEqual(world.detail, "orbit")

    def test_to_jump_point(self):
        world = StarSystemTestCase.system
        self.assertEqual(world.detail, "orbit")
        world.to_jump_point()
        self.assertEqual(world.detail, "jump")
        world.to_jump_point()
        self.assertEqual(world.detail, "jump")

    def test_from_jump_point(self):
        world = StarSystemTestCase.system
        world.detail = "jump"
        world.from_jump_point()
        self.assertEqual(world.detail, "orbit")
        world.from_jump_point()
        self.assertEqual(world.detail, "orbit")

    def test_join_trade(self):
        world = StarSystemTestCase.system
        world.detail = "surface"
        world.join_trade()
        self.assertEqual(world.detail, "trade")
        world.join_trade()
        self.assertEqual(world.detail, "trade")

    def test_leave_trade(self):
        world = StarSystemTestCase.system
        world.detail = "trade"
        world.leave_trade()
        self.assertEqual(world.detail, "surface")
        world.leave_trade()
        self.assertEqual(world.detail, "surface")
       

    # __eq__
    # __repr__
    # description
    # on_surface

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
