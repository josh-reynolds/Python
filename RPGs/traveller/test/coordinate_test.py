"""Contains tests for the coordinate module."""
import unittest
from src.coordinate import convert_3_axis, absolute, coordinate_from, Coordinate, create_3_axis

class CoordinateTestCase(unittest.TestCase):
    """Tests 3-axis Coordinate functions."""

    def test_convert_3_axis_even(self) -> None:
        """Test conversion of a three-axis coordinate to Traveller standard.

        These expected results are based on an even-numbered origin column.
        """
        coord = (0,0,0)
        self.assertEqual(convert_3_axis(coord, "even"), (0,0))

        coord = (-1,1,0)
        self.assertEqual(convert_3_axis(coord, "even"), (1,1))

        coord = (-1,2,-1)
        self.assertEqual(convert_3_axis(coord, "even"), (2,0))

        coord = (-1,3,-2)
        self.assertEqual(convert_3_axis(coord, "even"), (3,0))

        coord = (-2,3,-1)
        self.assertEqual(convert_3_axis(coord, "even"), (3,1))

        coord = (-3,6,-3)
        self.assertEqual(convert_3_axis(coord, "even"), (6,0))

        coord = (0,6,-6)
        self.assertEqual(convert_3_axis(coord, "even"), (6,-3))

        coord = (3,4,-7)
        self.assertEqual(convert_3_axis(coord, "even"), (4,-5))

        coord = (5,0,-5)
        self.assertEqual(convert_3_axis(coord, "even"), (0,-5))

        coord = (7,-4,-3)
        self.assertEqual(convert_3_axis(coord, "even"), (-4,-5))

        coord = (5,-5,0)
        self.assertEqual(convert_3_axis(coord, "even"), (-5,-2))

        coord = (2,-5,3)
        self.assertEqual(convert_3_axis(coord, "even"), (-5,1))

        coord = (0,-5,5)
        self.assertEqual(convert_3_axis(coord, "even"), (-5,3))

        coord = (-4,-3,7)
        self.assertEqual(convert_3_axis(coord, "even"), (-3,6))

        coord = (-5,0,5)
        self.assertEqual(convert_3_axis(coord, "even"), (0,5))

        coord = (-7,4,3)
        self.assertEqual(convert_3_axis(coord, "even"), (4,5))

        coord = (-6,6,0)
        self.assertEqual(convert_3_axis(coord, "even"), (6,3))

    def test_convert_3_axis_odd(self) -> None:
        """Test conversion of a three-axis coordinate to Traveller standard.

        These expected results are based on an odd-numbered origin column.
        """
        coord = (0,0,0)
        self.assertEqual(convert_3_axis(coord, "odd"), (0,0))

        coord = (-1,1,0)
        self.assertEqual(convert_3_axis(coord, "odd"), (1,0))

        coord = (0,1,-1)
        self.assertEqual(convert_3_axis(coord, "odd"), (1,-1))

        coord = (1,0,-1)
        self.assertEqual(convert_3_axis(coord, "odd"), (0,-1))

        coord = (1,-1,0)
        self.assertEqual(convert_3_axis(coord, "odd"), (-1,-1))

        coord = (0,-1,1)
        self.assertEqual(convert_3_axis(coord, "odd"), (-1,0))

    def test_subsector_placement(self) -> None:
        """Test conversion to absolute coordinates on a subsector map."""
        coord = (0,0,0)
        self.assertEqual(absolute(coord), ((1,1), (0,0)))

        coord = (-1,1,0)
        self.assertEqual(absolute(coord), ((2,1), (0,0)))

        coord = (-1,0,1)
        self.assertEqual(absolute(coord), ((1,2), (0,0)))

        coord = (0,-1,1)
        self.assertEqual(absolute(coord), ((8,1), (-1,0)))

        coord = (1,0,-1)
        self.assertEqual(absolute(coord), ((1,10), (0,-1)))

        coord = (-9,0,9)
        self.assertEqual(absolute(coord), ((1,10), (0,0)))

        coord = (-13,7,6)
        self.assertEqual(absolute(coord), ((8,10), (0,0)))

    def test_from_string(self) -> None:
        """Test importing a Coordinate from a string."""
        string = "(0,0,0)"
        actual = coordinate_from(string)
        expected = Coordinate(0,0,0)
        self.assertEqual(actual, expected)

        string = "(0,1,-1)"
        actual = coordinate_from(string)
        expected = Coordinate(0,1,-1)
        self.assertEqual(actual, expected)

        string = "(1,0,-1)"
        actual = coordinate_from(string)
        expected = Coordinate(1,0,-1)
        self.assertEqual(actual, expected)

        string = "(1,-1,0)"
        actual = coordinate_from(string)
        expected = Coordinate(1,-1,0)
        self.assertEqual(actual, expected)

        string = "(m,0,0)"
        with self.assertRaises(ValueError) as context:
            _ = coordinate_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        string = "(1.1,0,0)"
        with self.assertRaises(ValueError) as context:
            _ = coordinate_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: '1.1'")

        string = "(0,0,0,0)"
        with self.assertRaises(ValueError) as context:
            _ = coordinate_from(string)
        self.assertEqual(f"{context.exception}",
                         "string should have exactly 3 values: '4'")

        string = "(0,0)"
        with self.assertRaises(ValueError) as context:
            _ = coordinate_from(string)
        self.assertEqual(f"{context.exception}",
                         "string should have exactly 3 values: '2'")

        string = "[0,0,0)"
        with self.assertRaises(ValueError) as context:
            _ = coordinate_from(string)
        self.assertEqual(f"{context.exception}",
                         "string should be surrounded by parentheses: '[0,0,0)'")

        string = "(1,0,0)"
        with self.assertRaises(ValueError) as context:
            _ = coordinate_from(string)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate - should sum to zero: '(1,0,0)'")

        coord = Coordinate(-3,0,3)
        coord_string = f"{coord}"
        actual = coordinate_from(coord_string)
        self.assertEqual(actual, coord)

    def test_valid_coordinate(self) -> None:
        """Test validation of potential three-axis coordinates."""
        actual = Coordinate(0,0,0)
        self.assertTrue(actual.is_valid())

    def test_create_3_axis(self) -> None:
        """Test creation of a Coordinate given Traveller subsector coordinate values."""
        # basic conversion
        # all four quadrants of subsector coords
        # invalid column
        # invalid row
        # non-numeric data for any coord value
        actual = create_3_axis(1, 1, 0, 0)
        expected = Coordinate(0, 0, 0)
        self.assertEqual(actual, expected)

        actual = create_3_axis(2, 1, 0, 0)
        expected = Coordinate(-1, 1, 0)
        self.assertEqual(actual, expected)

        actual = create_3_axis(8, 8, -1, -1)
        expected = Coordinate(3, -1, -2)
        self.assertEqual(actual, expected)

        actual = create_3_axis(8, 9, -1, -1)
        expected = Coordinate(2, -1, -1)
        self.assertEqual(actual, expected)

        actual = create_3_axis(8, 1, -1, 0)
        expected = Coordinate(0, -1, 1)
        self.assertEqual(actual, expected)

        actual = create_3_axis(1, 10, 0, -1)
        expected = Coordinate(1, 0, -1)
        self.assertEqual(actual, expected)
