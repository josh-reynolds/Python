"""Contains classes to represent landscape features."""
import math
from random import randint
from typing import Tuple
from pvector import PVector
from screen_matrix import push_matrix, pop_matrix, translate, rotate, equilateral_triangle
from engine import screen
from constants import WIDTH, HEIGHT, FINGER, GROUND_LEVEL, STRATA_HEIGHT, BEAD
from constants import GOLD, MITHRIL, BORDER, SHOW_LABELS, MARGIN, CAVERN, WATER
from location import Cavern

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
    return PVector(randint(MARGIN, WIDTH-MARGIN), randint(GROUND_LEVEL+MARGIN, HEIGHT-MARGIN))

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

        self.corner_vector = PVector.normalize(PVector.sub(self.center, self.corner))
        self.angle = math.radians(self.corner_vector.heading()) + math.pi

        self.name = "Mithril"

    def update(self) -> None:
        """Update the Mithril object once per frame."""

    def draw(self) -> None:
        """Draw the Mithril object to the screen once per frame."""
        push_matrix()
        translate(self.center.x, self.center.y)
        rotate(self.angle)
        equilateral_triangle(self.radius, MITHRIL, 0)
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


class UndergroundRiver():
    """Represents an underground river generated during the Primordial Age."""

    def __init__(self) -> None:
        """Create an UndergroundRiver object."""
        self.vertices = []

        self.lakes = []
        self.caves = []

        self.name = "Underground River"

        current_x = 0
        current_y = strata_depth(randint(0,5))

        while current_x < WIDTH and GROUND_LEVEL < current_y < HEIGHT and current_y:
            self.vertices.append(PVector(current_x, current_y))
            current_x += FINGER

            check = randint(0,9)
            match check:
                case 0 | 1 | 2:
                    pass
                case 3 | 4:
                    current_y += STRATA_HEIGHT
                case 5 | 6:
                    current_y -= STRATA_HEIGHT
                case 7 | 8:
                    self.caves.append(Cavern(PVector(current_x, current_y), CAVERN, None, False, 0))
                case 9:
                    current_x -= FINGER
                    current_y += STRATA_HEIGHT // 2

            if current_y < GROUND_LEVEL:
                x_1, y_1 = self.vertices[-1].x, self.vertices[-1].y
                x_2, y_2 = current_x, current_y
                slope = (y_2 - y_1) / (x_2 - x_1)
                intercept = y_1 - (slope * x_1)

                lake_y = GROUND_LEVEL
                lake_x = (lake_y - intercept) / slope

                self.lakes.append(PVector(lake_x,lake_y))

        self.vertices.append(PVector(current_x, current_y))

    def update(self) -> None:
        """Update the UndergroundRiver's state once per frame."""

    def draw(self) -> None:
        """Draw the UndergroundRiver once per frame."""
        for lake in self.lakes:
            screen.draw.circle(lake.x, lake.y, BEAD, WATER, 0)

        for index,vertex in enumerate(self.vertices[:-1]):
            screen.draw.line(WATER,
                             (vertex.x, vertex.y),
                             (self.vertices[index+1].x, self.vertices[index+1].y),
                             8)
        if SHOW_LABELS:
            screen.draw.text(self.name, pos=(self.vertices[0].x, self.vertices[0].y))

class Stratum():
    """Represents a geologic layer underground."""

    def __init__(self, depth: int, color: Tuple[int,int,int]) -> None:
        """Create an instance of a Stratum object."""
        self.depth = depth
        self.color = color

        self.points = []
        self.points.append((0,self.depth))
        for i in range(5):
            self.points.append(((i+1) * WIDTH//5, self.depth + randint(-10,10)))
        self.points.append((WIDTH,self.depth))
        self.points.append((WIDTH,HEIGHT))
        self.points.append((0,HEIGHT))

    def draw(self) -> None:
        """Draw the Stratum to the screen once per frame."""
        screen.draw.polygon(self.points, self.color, 0)
