import unittest
class StarSystem:
    def __init__(self, name, coordinate, starport, size, atmosphere, 
                 hydrographics, population, government, law, tech, gas_giant=True):
        self.name = name
        self.coordinate = coordinate
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
        if self.detail == "surface":
            return f"on {self.name}"

        if self.detail == "orbit":
            return f"in orbit around {self.name}"

        if self.detail == "jump":
            return f"at the {self.name} jump point"

        if self.detail == "trade":
            return f"at the {self.name} trade depot"

        return "ERROR"    # should not be able to reach this point
                          # ensure there are only four (currently)
                          # possible values for self.detail?

    def on_surface(self):
        return self.detail in ('surface', 'trade')

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
        StarSystemTestCase.system = StarSystem("Test", (0,0,0), "A", 9, 9, 9, 9, 9, 9, 9, True)

    def test_coordinates(self):
        world = StarSystemTestCase.system
        self.assertTrue(type(world.coordinate) is tuple)

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

    def test_world_string(self):
        world = StarSystemTestCase.system
        self.assertEqual(f"{world}", "(0, 0, 0) - Test - A999999-9 In - G")

    def test_description(self):
        world = StarSystemTestCase.system

        world.detail = "surface"
        self.assertEqual(world.description(), "on Test")

        world.detail = "orbit"
        self.assertEqual(world.description(), "in orbit around Test")

        world.detail = "jump"
        self.assertEqual(world.description(), "at the Test jump point")

        world.detail = "trade"
        self.assertEqual(world.description(), "at the Test trade depot")

    def test_on_surface(self):
        world = StarSystemTestCase.system

        world.detail = "surface"
        self.assertTrue(world.on_surface())

        world.detail = "trade"
        self.assertTrue(world.on_surface())

        world.detail = "orbit"
        self.assertFalse(world.on_surface())

        world.detail = "jump"
        self.assertFalse(world.on_surface())

    def test_equality(self):
        world1 = StarSystemTestCase.system
        world2 = StarSystem("Test", (0,0,0), "A", 9, 9, 9, 9, 9, 9, 9, True)
        world3 = StarSystem("Foo", (0,0,0), "A", 9, 9, 9, 9, 9, 9, 9, True)

        self.assertEqual(world1, world2)
        self.assertNotEqual(world1, world3)

        world2.coordinate = 000
        self.assertNotEqual(world1, world2)

    def test_trade_modifiers(self):
        ag_world = StarSystem("Agricultural", (0,0,0), "A", 8, 5, 5, 7, 5, 5, 9, True)
        self.assertTrue(ag_world.agricultural)
        self.assertEqual(f"{ag_world}", "(0, 0, 0) - Agricultural - A855755-9 Ag - G")

        na_world = StarSystem("Non-agricultural", (0,0,0), "A", 8, 0, 3, 7, 5, 5, 9, True)
        self.assertTrue(na_world.nonagricultural)
        self.assertEqual(f"{na_world}", "(0, 0, 0) - Non-agricultural - A803755-9 Na - G")

        in_world = StarSystem("Industrial", (0,0,0), "A", 8, 7, 5, 9, 5, 5, 9, True)
        self.assertTrue(in_world.industrial)
        self.assertEqual(f"{in_world}", "(0, 0, 0) - Industrial - A875955-9 In - G")

        ni_world = StarSystem("Non-industrial", (0,0,0), "A", 8, 3, 5, 5, 5, 5, 9, True)
        self.assertTrue(ni_world.nonindustrial)
        self.assertEqual(f"{ni_world}", "(0, 0, 0) - Non-industrial - A835555-9 Ni - G")

        ri_world = StarSystem("Rich", (0,0,0), "A", 8, 6, 5, 8, 5, 5, 9, True)
        self.assertTrue(ri_world.rich)
        self.assertEqual(f"{ri_world}", "(0, 0, 0) - Rich - A865855-9 Ri - G")

        po_world = StarSystem("Poor", (0,0,0), "A", 8, 4, 0, 7, 5, 5, 9, True)
        self.assertTrue(po_world.poor)
        self.assertEqual(f"{po_world}", "(0, 0, 0) - Poor - A840755-9 Po - G")

        plain_world = StarSystem("Plain", (0,0,0), "A", 8, 3, 5, 7, 5, 5, 9, True)
        self.assertEqual(f"{plain_world}", "(0, 0, 0) - Plain - A835755-9 - G")

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
