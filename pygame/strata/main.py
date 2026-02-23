"""Draw randomly varying layers across the screen."""
from random import randint
from engine import screen, run
# pylint: disable=W0611
# W0611: Unused TITLE imported from constants (unused-import)
from constants import WIDTH, HEIGHT, TITLE, STRATA_HEIGHT

DEPTH = 150

points = []
points.append((0,DEPTH))
for i in range(5):
    points.append(((i+1) * WIDTH//5, DEPTH + randint(-10,10)))
points.append((WIDTH,DEPTH))
points.append((WIDTH,HEIGHT))
points.append((0,HEIGHT))

def update() -> None:
    """Update game state once per frame."""

def draw() -> None:
    """Draw the game screen once per frame."""
    screen.fill((80,80,220))

    screen.draw.polygon(points, (105,99,39), 0)


run()
