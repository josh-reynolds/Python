"""Contains functions to test for line segment intersections."""
from typing import Tuple
from pygame import Rect
from pvector import PVector

def segments_intersect(line_1: Tuple[PVector, PVector], line_2: Tuple[PVector, PVector]) -> bool:
    """Test whether two line segments intersect between their endpoints."""
    r = PVector.sub(line_1[1], line_1[0])
    s = PVector.sub(line_2[1], line_2[0])

    n = PVector.sub(line_2[0], line_1[0])

    u_numerator = n.cross(r)
    denominator = r.cross(s)

    if u_numerator == 0 and denominator == 0:
        # collinear case

        # endpoints touch
        if (line_1[0] == line_2[0] or line_1[0] == line_2[1]
            or line_1[1] == line_2[0] or line_1[1] == line_2[1]):
            return True

        # overlapping segments
        # segments overlap if their projection onto the x axis overlap
        # (or y axis if lines are vertical)

        # projection of AB is:
        # [min(A.x, B.x), max(A.x, B.x)]

        if line_1[0].x != line_1[1].x:     # lines are not vertical
            projection_1 = (min(line_1[0].x, line_1[1].x),
                            max(line_1[0].x, line_1[1].x))

            projection_2 = (min(line_2[0].x, line_2[1].x),
                            max(line_2[0].x, line_2[1].x))

        else:
            projection_1 = (min(line_1[0].y, line_1[1].y),
                            max(line_1[0].y, line_1[1].y))

            projection_2 = (min(line_2[0].y, line_2[1].y),
                            max(line_2[0].y, line_2[1].y))

        return projection_1[0] < projection_2[1] and projection_1[1] > projection_2[0]


    if denominator == 0:
        # parallel case
        return False

    u = u_numerator / denominator
    t = n.cross(s) / denominator

    return t >= 0 and t <= 1 and u >= 0 and u <= 1

# TO_DO: special case - line segment entirely inside the rect
def rect_segment_intersects(rect: Rect, segment: Tuple) -> bool:
    """Test whether a line segment intersects a rectangle."""
    top_left = PVector(rect.x, rect.y)
    top_right = PVector(rect.x + rect.w, rect.y)
    bottom_right = PVector(rect.x + rect.w, rect.y + rect.h)
    bottom_left = PVector(rect.x, rect.y + rect.h)

    top = (top_left, top_right)
    right = (top_right, bottom_right)
    bottom = (bottom_right, bottom_left)
    left = (bottom_left, top_left)

    result = False
    for edge in (top, right, bottom, left):
        if segments_intersect(edge, segment):
            result = True

    return result
