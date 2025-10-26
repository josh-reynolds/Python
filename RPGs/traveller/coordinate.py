"""Contains three-axis coordinate definition and methods to convert and manage them."""
from typing import Tuple

Coordinate = Tuple[int, int, int]

def convert_3_axis(coord: Coordinate) -> Tuple[int, int]:
    """Convert a three-axis coordinate to Traveller grid coordinates."""
    new_column = coord[1]
    column_offset = int(coord[1]/2)
    new_row_right =  -coord[0] - column_offset
    new_row_left =  coord[2] + column_offset

    if coord[1] > 0:
        return (new_column, new_row_right)
    return (new_column, new_row_left)

def absolute(coord: Coordinate) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Convert a three-axis coordinate to a position on a subsector map.

    Return values are the coordinates within the subsector (ranging from
    (1,1) to (8,10)) followed by the coordinates of the subsector itself.
    """
    return ((1,1), (0,0))
