"""Contains classes to represent landscape features."""
import math
from random import randint
from pvector import PVector
from screen_matrix import push_matrix, pop_matrix, translate, rotate, equilateral_triangle
from engine import screen
from constants import WIDTH, HEIGHT, FINGER, GROUND_LEVEL, STRATA_HEIGHT
from constants import GOLD, MITHRIL, BORDER, SHOW_LABELS

def nearest_corner(point: PVector) -> PVector:
    """Return the nearest screen corner to the given point."""
    if point.x < WIDTH/2:
        if point.y < HEIGHT/2:
            return PVector(0, 0)
        return PVector(0, HEIGHT)
    if point.y < HEIGHT/2:
        return PVector(WIDTH, 0)
    return PVector(WIDTH, HEIGHT)

def get_random_underground_location() -> PVector:
    """Return a random point in the underground region of the screen."""
    return PVector(randint(0, WIDTH), randint(GROUND_LEVEL, HEIGHT))

def strata_depth(strata: int) -> int:
    """Calculate and return the depth in pixels of a given strata layer."""
    return GROUND_LEVEL + STRATA_HEIGHT * strata + STRATA_HEIGHT//2

class Mithril():
    """Represents a Mithril deposit."""

    def __init__(self) -> None:
        """Create an instance of a Mithril object."""
        self.center = get_random_underground_location()
        self.radius = FINGER // 2
        self.corner = nearest_corner(self.center)

        corner_vector = PVector.normalize(PVector.sub(self.center, self.corner))
        self.angle = math.radians(corner_vector.heading()) + math.pi

        self.name = "Mithril"

    def update(self) -> None:
        """Update the Mithril object once per frame."""

    def draw(self) -> None:
        """Draw the Mithril object to the screen once per frame."""
        push_matrix()
        translate(self.center.x, self.center.y)
        rotate(self.angle)
        equilateral_triangle(self.radius, MITHRIL, 0)
        equilateral_triangle(self.radius, BORDER, 2)
        pop_matrix()

        if SHOW_LABELS:
            screen.draw.text(self.name, center=(self.center.x, self.center.y))

class GoldVein():
    """Represents a GoldVein deposit."""

    def __init__(self) -> None:
        """Create an instance of a GoldVein object."""
        self.left = PVector(0, strata_depth(randint(0,5)))
        self.right = PVector(WIDTH, strata_depth(randint(0,5)))
        self.midpoint = PVector(WIDTH//2,
                                (self.right.y - self.left.y)//2 + self.left.y)
        self.name = "Gold Vein"

    def update(self) -> None:
        """Update the GoldVein object once per frame."""

    def draw(self) -> None:
        """Draw the GoldVein object to the screen once per frame."""
        screen.draw.line(GOLD,
                         (self.left.x, self.left.y),
                         (self.right.x, self.right.y),
                         8)
        if SHOW_LABELS:
            screen.draw.text(self.name, center=(self.midpoint.x, self.midpoint.y))
