"""Contains tests for the coordinate module."""
import unittest
from coordinate import convert_3_axis

class CoordinateTestCase(unittest.TestCase):
    """Tests 3-axis Coordinate functions."""

    def test_convert_3_axis(self) -> None:
        """Test conversion of a three-axis coordinate to Traveller standard."""
        coord = (0,0,0)
        self.assertEqual(convert_3_axis(coord), (0,0))

        coord = (-3,6,-3)
        self.assertEqual(convert_3_axis(coord), (6,0))

        coord = (0,6,-6)
        self.assertEqual(convert_3_axis(coord), (6,-3))

        coord = (3,4,-7)
        self.assertEqual(convert_3_axis(coord), (4,-5))

        coord = (5,0,-5)
        self.assertEqual(convert_3_axis(coord), (0,-5))

        coord = (7,-4,-3)
        self.assertEqual(convert_3_axis(coord), (-4,-5))

        coord = (5,-5,0)
        self.assertEqual(convert_3_axis(coord), (-5,-2))

        coord = (2,-5,3)
        self.assertEqual(convert_3_axis(coord), (-5,1))

        coord = (0,-5,5)
        self.assertEqual(convert_3_axis(coord), (-5,3))

        coord = (-4,-3,7)
        self.assertEqual(convert_3_axis(coord), (-3,6))

        coord = (-5,0,5)
        self.assertEqual(convert_3_axis(coord), (0,5))

        coord = (-7,4,3)
        self.assertEqual(convert_3_axis(coord), (4,5))

        coord = (-6,6,0)
        self.assertEqual(convert_3_axis(coord), (6,3))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
