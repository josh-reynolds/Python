"""Draw randomly varying layers across the screen."""
from random import randint
from engine import screen, run
# pylint: disable=W0611
# W0611: Unused TITLE imported from constants (unused-import)
from constants import WIDTH, HEIGHT, TITLE, STRATA_HEIGHT

depth = 150
points = []
points.append((0,depth))
for i in range(5):
    points.append(((i+1) * WIDTH//5, depth + randint(-10,10)))
points.append((WIDTH,depth))
points.append((WIDTH,HEIGHT))
points.append((0,HEIGHT))

depth = 250
points_2 = []
points_2.append((0,depth))
for i in range(5):
    points_2.append(((i+1) * WIDTH//5, depth + randint(-10,10)))
points_2.append((WIDTH,depth))
points_2.append((WIDTH,HEIGHT))
points_2.append((0,HEIGHT))

def update() -> None:
    """Update game state once per frame."""

def draw() -> None:
    """Draw the game screen once per frame."""
    screen.fill((80,80,220))

    screen.draw.polygon(points, (105,99,39), 0)
    screen.draw.polygon(points_2, (137,131,75), 0)


run()
