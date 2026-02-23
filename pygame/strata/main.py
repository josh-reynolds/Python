"""Draw randomly varying layers across the screen."""
from random import randint
from typing import Tuple
from engine import screen, run
# pylint: disable=W0611
# W0611: Unused TITLE imported from constants (unused-import)
from constants import WIDTH, HEIGHT, TITLE, STRATA_HEIGHT


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


strata = []
strata.append(Stratum(150, (105,99,39)))
strata.append(Stratum(250, (137,131,75)))

def update() -> None:
    """Update game state once per frame."""

def draw() -> None:
    """Draw the game screen once per frame."""
    screen.fill((80,80,220))

    screen.draw.polygon(strata[0].points, strata[0].color, 0)
    screen.draw.polygon(strata[1].points, strata[1].color, 0)


run()
