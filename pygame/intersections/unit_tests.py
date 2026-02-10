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
        """Tests non-intersecting non-parallel lines."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(250, 50), PVector(250, 150))
        self.assertFalse(segments_intersect(line_1, line_2))

    def test_touch_at_endpoint(self) -> None:
        """Tests line segments touching at one endpoint."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(150, 50), PVector(150, 100))
        self.assertTrue(segments_intersect(line_1, line_2))

    def test_parallel_lines(self) -> None:
        """Tests parallel line (non-) intersection."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(100, 200), PVector(200, 200))
        self.assertFalse(segments_intersect(line_1, line_2))

    def test_non_overlapping_collinear_lines(self) -> None:
        """Tests collinear line segments that do not overlap."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(300, 100), PVector(400, 100))
        self.assertFalse(segments_intersect(line_1, line_2))

    def test_collinear_enpoints_touching(self) -> None:
        """Tests collinear line segments that touch at an endpoint."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(200, 100), PVector(300, 100))
        self.assertTrue(segments_intersect(line_1, line_2))

    def test_overlapping_collinear_lines(self) -> None:
        """Tests collinear line segments that overlap."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(150, 100), PVector(250, 100))
        self.assertTrue(segments_intersect(line_1, line_2))

    def test_collinear_lines_entirely_overlapping(self) -> None:
        """Tests line segment containing a collinear line segment."""
        line_1 = (PVector(100, 100), PVector(200, 100))
        line_2 = (PVector(125, 100), PVector(150, 100))
        self.assertTrue(segments_intersect(line_1, line_2))

# line-line intersections ----------------
# [OK] parallel
# [OK] collinear - no overlap
# [OK] collinear - touch at endpoint
# [OK] collinear - overlap
# [OK] collinear - line contained within line
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
