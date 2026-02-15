"""Contains classes to represent landscape features."""
import math
from random import randint
from pvector import PVector
from screen_matrix import push_matrix, pop_matrix, translate, rotate, equilateral_triangle
from engine import screen

# duplicated from main
WIDTH = 1100
HEIGHT = 850
FINGER = HEIGHT // 5
GROUND_LEVEL = HEIGHT // 5
STRATA_HEIGHT = (HEIGHT - GROUND_LEVEL) // 6
GOLD = (255, 255, 0)
MITHRIL = (255,255,255)
BORDER = (0, 0, 0)

# TO_DO: broken now that we split across modules, fix!
show_labels = False

def nearest_corner(point: PVector) -> PVector:
    if point.x < WIDTH/2:
        if point.y < HEIGHT/2:
            return PVector(0, 0)
        return PVector(0, HEIGHT)
    if point.y < HEIGHT/2:
        return PVector(WIDTH, 0)
    return PVector(WIDTH, HEIGHT)

def get_random_underground_location() -> PVector:
    return PVector(randint(0, WIDTH), randint(GROUND_LEVEL, HEIGHT))

def strata_depth(strata: int) -> int:
    return GROUND_LEVEL + STRATA_HEIGHT * strata + STRATA_HEIGHT//2

class Mithril():
    def __init__(self) -> None:
        self.center = get_random_underground_location()
        self.radius = FINGER // 2
        self.corner = nearest_corner(self.center)

        corner_vector = PVector.normalize(PVector.sub(self.center, self.corner))
        self.angle = math.radians(corner_vector.heading()) + math.pi

        self.name = "Mithril"

    def update(self) -> None:
        pass

    def draw(self) -> None:
        push_matrix()
        translate(self.center.x, self.center.y)
        rotate(self.angle)
        equilateral_triangle(self.radius, MITHRIL, 0)
        equilateral_triangle(self.radius, BORDER, 2)
        pop_matrix()

        if show_labels:
            screen.draw.text(self.name, center=(self.center.x, self.center.y))

class GoldVein():
    def __init__(self) -> None:
        self.left = PVector(0, strata_depth(randint(0,5)))
        self.right = PVector(WIDTH, strata_depth(randint(0,5)))
        self.midpoint = PVector(WIDTH//2, 
                                (self.right.y - self.left.y)//2 + self.left.y)
        self.name = "Gold Vein"

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen.draw.line(GOLD, 
                         (self.left.x, self.left.y),
                         (self.right.x, self.right.y),
                         8)
        if show_labels:
            screen.draw.text(self.name, center=(self.midpoint.x, self.midpoint.y))
