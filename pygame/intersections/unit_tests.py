"""Contains tests for the intersections functions."""
import unittest
from pvector import PVector
from intersections import segments_intersect, rect_segment_intersects

class SegmentIntersectionTestCase(unittest.TestCase):
    """Tests intersection of line segments."""

    def test_intersections(self) -> None:
        """Tests simple line segment intersection."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(150, 50), PVector(150, 150))
        self.assertTrue(segments_intersect(line_1, line_2))

def suite():
    """Create a suite of test cases."""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromName('unit_tests'))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
