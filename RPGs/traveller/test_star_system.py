"""Contains tests for the star_map module."""
import unittest
from star_system import StarSystem

class StarSystemTestCase(unittest.TestCase):
    """Tests StarSystem class."""
    def setUp(self):
        StarSystemTestCase.system = StarSystem("Test", (0,0,0), "A", 9, 9, 9, 9, 9, 9, 9, True)

    def test_coordinates(self):
        world = StarSystemTestCase.system
        self.assertTrue(isinstance(world.coordinate, tuple))

    def test_landing(self):
        world = StarSystemTestCase.system
        self.assertEqual(world.detail, "orbit")
        world.land()
        self.assertEqual(world.detail, "starport")
        world.land()
        self.assertEqual(world.detail, "starport")

    def test_liftoff(self):
        world = StarSystemTestCase.system
        world.detail = "starport"
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
        world.detail = "starport"
        world.join_trade()
        self.assertEqual(world.detail, "trade")
        world.join_trade()
        self.assertEqual(world.detail, "trade")

    def test_leave_trade(self):
        world = StarSystemTestCase.system
        world.detail = "trade"
        world.leave_trade()
        self.assertEqual(world.detail, "starport")
        world.leave_trade()
        self.assertEqual(world.detail, "starport")

    def test_world_string(self):
        world = StarSystemTestCase.system
        self.assertEqual(f"{world}", "(0, 0, 0) - Test - A999999-9 In - G")

    def test_description(self):
        world = StarSystemTestCase.system

        world.detail = "starport"
        self.assertEqual(world.description(), "at the Test starport")

        world.detail = "orbit"
        self.assertEqual(world.description(), "in orbit around Test")

        world.detail = "jump"
        self.assertEqual(world.description(), "at the Test jump point")

        world.detail = "trade"
        self.assertEqual(world.description(), "at the Test trade depot")

        world.detail = "terminal"
        self.assertEqual(world.description(), "at the Test passenger terminal")

    def test_on_surface(self):
        world = StarSystemTestCase.system

        world.detail = "starport"
        self.assertTrue(world.on_surface())

        world.detail = "trade"
        self.assertTrue(world.on_surface())

        world.detail = "terminal"
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
