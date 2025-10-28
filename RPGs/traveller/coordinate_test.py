"""Contains tests for the coordinate module."""
import unittest
from coordinate import convert_3_axis, absolute, Coordinate

class CoordinateTestCase(unittest.TestCase):
    """Tests 3-axis Coordinate functions."""

    def test_convert_3_axis_even(self) -> None:
        """Test conversion of a three-axis coordinate to Traveller standard.

        These expected results are based on an even-numbered origin column.
        """
        coord = Coordinate(0,0,0)
        self.assertEqual(convert_3_axis(coord, "even"), (0,0))

        coord = Coordinate(-1,1,0)
        self.assertEqual(convert_3_axis(coord, "even"), (1,1))

        coord = Coordinate(-1,2,-1)
        self.assertEqual(convert_3_axis(coord, "even"), (2,0))

        coord = Coordinate(-1,3,-2)
        self.assertEqual(convert_3_axis(coord, "even"), (3,0))

        coord = Coordinate(-2,3,-1)
        self.assertEqual(convert_3_axis(coord, "even"), (3,1))

        coord = Coordinate(-3,6,-3)
        self.assertEqual(convert_3_axis(coord, "even"), (6,0))

        coord = Coordinate(0,6,-6)
        self.assertEqual(convert_3_axis(coord, "even"), (6,-3))

        coord = Coordinate(3,4,-7)
        self.assertEqual(convert_3_axis(coord, "even"), (4,-5))

        coord = Coordinate(5,0,-5)
        self.assertEqual(convert_3_axis(coord, "even"), (0,-5))

        coord = Coordinate(7,-4,-3)
        self.assertEqual(convert_3_axis(coord, "even"), (-4,-5))

        coord = Coordinate(5,-5,0)
        self.assertEqual(convert_3_axis(coord, "even"), (-5,-2))

        coord = Coordinate(2,-5,3)
        self.assertEqual(convert_3_axis(coord, "even"), (-5,1))

        coord = Coordinate(0,-5,5)
        self.assertEqual(convert_3_axis(coord, "even"), (-5,3))

        coord = Coordinate(-4,-3,7)
        self.assertEqual(convert_3_axis(coord, "even"), (-3,6))

        coord = Coordinate(-5,0,5)
        self.assertEqual(convert_3_axis(coord, "even"), (0,5))

        coord = Coordinate(-7,4,3)
        self.assertEqual(convert_3_axis(coord, "even"), (4,5))

        coord = Coordinate(-6,6,0)
        self.assertEqual(convert_3_axis(coord, "even"), (6,3))

    def test_convert_3_axis_odd(self) -> None:
        """Test conversion of a three-axis coordinate to Traveller standard.

        These expected results are based on an odd-numbered origin column.
        """
        coord = Coordinate(0,0,0)
        self.assertEqual(convert_3_axis(coord, "odd"), (0,0))

        coord = Coordinate(-1,1,0)
        self.assertEqual(convert_3_axis(coord, "odd"), (1,0))

        coord = Coordinate(0,1,-1)
        self.assertEqual(convert_3_axis(coord, "odd"), (1,-1))

        coord = Coordinate(1,0,-1)
        self.assertEqual(convert_3_axis(coord, "odd"), (0,-1))

        coord = Coordinate(1,-1,0)
        self.assertEqual(convert_3_axis(coord, "odd"), (-1,-1))

        coord = Coordinate(0,-1,1)
        self.assertEqual(convert_3_axis(coord, "odd"), (-1,0))

    def test_subsector_placement(self) -> None:
        """Test conversion to absolute coordinates on a subsector map."""
        coord = Coordinate(0,0,0)
        self.assertEqual(absolute(coord), ((1,1), (0,0)))

        coord = Coordinate(-1,1,0)
        self.assertEqual(absolute(coord), ((2,1), (0,0)))

        coord = Coordinate(-1,0,1)
        self.assertEqual(absolute(coord), ((1,2), (0,0)))

        coord = Coordinate(0,-1,1)
        self.assertEqual(absolute(coord), ((8,1), (-1,0)))

        coord = Coordinate(1,0,-1)
        self.assertEqual(absolute(coord), ((1,10), (0,-1)))

        coord = Coordinate(-9,0,9)
        self.assertEqual(absolute(coord), ((1,10), (0,0)))

        coord = Coordinate(-13,7,6)
        self.assertEqual(absolute(coord), ((8,10), (0,0)))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
