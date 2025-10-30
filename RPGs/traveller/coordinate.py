"""Contains three-axis coordinate definition and methods to convert and manage them."""
from typing import Tuple, Any, Iterator

class Coordinate:
    """Represents a 3-axis coordinate on a hex grid."""

    def __init__(self, first: int, second: int, third: int) -> None:
        """Create an instance of a Coordinate."""
        self.coords = (first, second, third)
        self.trav_coord = absolute(self.coords)

    def __getitem__(self, index: int) -> int:
        """Return one of the Coordinate's three values."""
        return self.coords[index]

    def __str__(self) -> str:
        """Return string representation of a Coordinate object."""
        return f"{self.coords} | {self.trav_coord}"

    def __repr__(self) -> str:
        """Return the developer string representation of a Coordinate object."""
        return f"Coordinate({self[0]}, {self[1]}, {self[2]})"

    def __eq__(self, other: Any) -> bool:
        """Test if two Coordinates are equal."""
        if type(other) is type(self):
            return self[0] == other[0] and self[1] == other[1] and self[2] == other[2]
        return NotImplemented

    def __hash__(self) -> int:
        """Calculate the hash value for a Coordinate object."""
        return hash(self.coords)

    def __lt__(self, other: Any) -> bool:
        """Test if one Coordinate is greater than another."""
        if type(other) is type(self):
            return self.coords < other.coords
        return NotImplemented

    def __iter__(self) -> Iterator:
        """Return an iterator over coordinate values."""
        return iter(self.coords)

    def is_valid(self) -> bool:
        """Test whether a self.coords tuple is a valid three-axis coordinate."""
        return sum(self.coords) == 0


def convert_3_axis(coord: Tuple[int, int, int], origin_column: str = "odd") -> Tuple[int, int]:
    """Convert a three-axis coordinate to Traveller grid coordinates."""
    new_column = coord[1]
    column_offset = int(coord[1]/2)

    adjust = 0
    if origin_column == "odd" and new_column % 2 == 1:
        adjust = -1

    new_row_right =  -coord[0] - column_offset + adjust
    new_row_left =  coord[2] + column_offset + adjust

    if coord[1] > 0:
        return (new_column, new_row_right)
    return (new_column, new_row_left)

# TO_DO: may want to rework how we handle origin and column here
#        for now we'll stick with the assumption it is fixed at (1,1)
def absolute(coord: Tuple[int, int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Convert a three-axis coordinate to a position on a subsector map.

    Return values are the coordinates within the subsector (ranging from
    (1,1) to (8,10)) followed by the coordinates of the subsector itself.

    The origin point is (1,1), so we need to tell convert_3_axis() to use
    an odd column number.
    """
    two_axis = convert_3_axis(coord, "odd")

    x_offset = two_axis[0] // 8
    x_precision = two_axis[0] % 8 + 1

    y_offset = two_axis[1] // 10
    y_precision = two_axis[1] % 10 + 1

    return ((x_precision, y_precision), (x_offset, y_offset))

def coordinate_from(string: str) -> Coordinate:
    """Create a Coordinate object from a string representation.

    String format is (d,d,d)
    Digits are positive or negative integers.
    """
    contents = string[1:-1]     # strip enclosing parens
    digits = contents.split(',')

    if len(digits) != 3:
        raise ValueError(f"string should have exactly 3 values: '{len(digits)}'")

    if string[0] != '(' or string[-1] != ')':
        raise ValueError(f"string should be surrounded by parentheses: '{string}'")

    return Coordinate(int(digits[0]),
                      int(digits[1]),
                      int(digits[2]))
