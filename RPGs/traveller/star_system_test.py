"""Contains tests for the star_map module."""
import unittest
from coordinate import Coordinate
from star_system import StarSystem, UWP, uwp_from, star_system_from

class StarSystemTestCase(unittest.TestCase):
    """Tests StarSystem class."""

    system: StarSystem

    def setUp(self) -> None:
        """Create a fixture for testing the StarSystem class."""
        uwp = UWP("A", 9, 9, 9, 9, 9, 9, 9)
        StarSystemTestCase.system = StarSystem("Test", Coordinate(0,0,0), uwp, True)

    def test_coordinates(self) -> None:
        """Test the coordinate property of a StarSystem class."""
        world = StarSystemTestCase.system
        self.assertTrue(isinstance(world.coordinate, Coordinate))
        self.assertEqual(world.coordinate, Coordinate(0,0,0))

    def test_world_string(self) -> None:
        """Test the string representation of a StarSystem object."""
        world = StarSystemTestCase.system
        self.assertEqual(f"{world}", "Test - A999999-9 In - G")

    def test_description(self) -> None:
        """Test the descriptive location string of a StarSystem object."""
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

    def test_on_surface(self) -> None:
        """Test detection of whether the player is on the world's surface."""
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

    def test_equality(self) -> None:
        """Test for equivalence between two StarSystems."""
        world1 = StarSystemTestCase.system
        uwp = UWP("A", 9, 9, 9, 9, 9, 9, 9)
        world2 = StarSystem("Test", Coordinate(0,0,0), uwp, True)
        world3 = StarSystem("Foo", Coordinate(0,0,0), uwp, True)

        self.assertEqual(world1, world2)
        self.assertNotEqual(world1, world3)

        world2.coordinate = Coordinate(1,0,0)
        self.assertNotEqual(world1, world2)

    def test_trade_modifiers(self) -> None:
        """Test determination of trade modifiers for a StarSystem object."""
        uwp = UWP("A", 8, 5, 5, 7, 5, 5, 9)
        ag_world = StarSystem("Agricultural", Coordinate(0,0,0), uwp, True)
        self.assertTrue(ag_world.agricultural)
        self.assertEqual(f"{ag_world}",
                         "Agricultural - A855755-9 Ag - G")

        uwp = UWP("A", 8, 0, 3, 7, 5, 5, 9)
        na_world = StarSystem("Non-agricultural", Coordinate(0,0,0), uwp, True)
        self.assertTrue(na_world.nonagricultural)
        self.assertEqual(f"{na_world}",
                         "Non-agricultural - A803755-9 Na - G")

        uwp = UWP("A", 8, 7, 5, 9, 5, 5, 9)
        in_world = StarSystem("Industrial", Coordinate(0,0,0), uwp, True)
        self.assertTrue(in_world.industrial)
        self.assertEqual(f"{in_world}",
                         "Industrial - A875955-9 In - G")

        uwp = UWP("A", 8, 3, 5, 5, 5, 5, 9)
        ni_world = StarSystem("Non-industrial", Coordinate(0,0,0), uwp, True)
        self.assertTrue(ni_world.nonindustrial)
        self.assertEqual(f"{ni_world}",
                         "Non-industrial - A835555-9 Ni - G")

        uwp = UWP("A", 8, 6, 5, 8, 5, 5, 9)
        ri_world = StarSystem("Rich", Coordinate(0,0,0), uwp, True)
        self.assertTrue(ri_world.rich)
        self.assertEqual(f"{ri_world}",
                         "Rich - A865855-9 Ri - G")

        uwp = UWP("A", 8, 4, 0, 7, 5, 5, 9)
        po_world = StarSystem("Poor", Coordinate(0,0,0), uwp, True)
        self.assertTrue(po_world.poor)
        self.assertEqual(f"{po_world}",
                         "Poor - A840755-9 Po - G")

        uwp = UWP("A", 8, 3, 5, 7, 5, 5, 9)
        plain_world = StarSystem("Plain", Coordinate(0,0,0), uwp, True)
        self.assertEqual(f"{plain_world}",
                         "Plain - A835755-9 - G")

    def test_from_string(self) -> None:
        """Test importing a StarSystem from a string."""
        string = "(0, 0, 0) - Yorbund - A875955-A In - G"
        actual = star_system_from(string)
        expected = StarSystem("Yorbund",
                              Coordinate(0,0,0),
                              UWP('A', 8, 7, 5, 9, 5, 5, 10),
                              True)
        self.assertEqual(actual, expected)

        string = "(-1, 1, 0) - Aramis - A865855-A Ri - G"
        actual = star_system_from(string)
        expected = StarSystem("Aramis",
                              Coordinate(-1,1,0),
                              UWP('A', 8, 6, 5, 8, 5, 5, 10),
                              True)
        self.assertEqual(actual, expected)

        string = "(-2, -1, 3) - Glisten Base - B8A5322-8 Ni"
        actual = star_system_from(string)
        expected = StarSystem("Glisten Base",
                              Coordinate(-2,-1,3),
                              UWP('B', 8, 10, 5, 3, 2, 2, 8),
                              False)
        self.assertEqual(actual, expected)

        # missing trade codes
        # multiple trade codes
        # invalid coordinates
        # invalid UWP
        # string too long
        # string too short


class UWPTestCase(unittest.TestCase):
    """Tests UWP class."""

    def test_from_string(self) -> None:
        """Test importing a UWP from a string."""
        string = "A123456-7"
        actual = uwp_from(string)
        expected = UWP('A', 1, 2, 3, 4, 5, 6, 7)
        self.assertEqual(actual, expected)

        string = "A877777-7"
        actual = uwp_from(string)
        expected = UWP('A', 8, 7, 7, 7, 7, 7, 7)
        self.assertEqual(actual, expected)

        string = "AAAAAAA-A"
        actual = uwp_from(string)
        expected = UWP('A', 10, 10, 10, 10, 10, 10, 10)
        self.assertEqual(actual, expected)

        string = "AG77777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 16: 'G'")

        string = "M777777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for starport: 'M'")

        string = "A7777777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "string length should be exactly 9 characters: 10")

        string = "A77777-7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "string length should be exactly 9 characters: 8")

        string = "A777777!7"
        with self.assertRaises(ValueError) as context:
            _ = uwp_from(string)
        self.assertEqual(f"{context.exception}",
                         "tech level should be separated by a '-' character: '!'")

        uwp = UWP('A', 1, 2, 3, 4, 5, 6, 7)
        uwp_string = f"{uwp}"
        actual = uwp_from(uwp_string)
        self.assertEqual(actual, uwp)

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
