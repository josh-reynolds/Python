"""Contains tests for the intersections functions."""
import unittest
from pvector import PVector
from intersections import segments_intersect, rect_segment_intersects

class SegmentIntersectionTestCase(unittest.TestCase):
    """Tests intersection of line segments."""

    def test_intersect_within_segments(self) -> None:
        """Tests simple line segment intersection."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(150, 50), PVector(150, 150))
        self.assertTrue(segments_intersect(line_1, line_2))

    def test_no_intersect_within_segments(self) -> None:
        """Tests simple line segment intersection."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(250, 50), PVector(250, 150))
        self.assertFalse(segments_intersect(line_1, line_2))

    def test_touch_at_endpoint(self) -> None:
        """Tests simple line segment intersection."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(150, 50), PVector(150, 100))
        self.assertTrue(segments_intersect(line_1, line_2))

# line-line intersections ----------------
# [  ] parallel
# [  ] collinear - no overlap
# [  ] collinear - touch at endpoint
# [  ] collinear - overlap
# [  ] collinear - line contained within line
# [OK] intersect - touch at an endpoint
# [OK] intersect within segments
# [OK] does not intersect within segments
# 
# should we check different slopes? horizontal, vertical, positive, negative?

# rect-line intersections ----------------
# [  ] does not intersect
# [  ] intersects top
# [  ] intersects right
# [  ] intersects bottom
# [  ] intersects left
# [  ] segment inside rect

def suite():
    """Create a suite of test cases."""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromName('unit_tests'))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
