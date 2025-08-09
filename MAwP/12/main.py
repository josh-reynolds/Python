"""Chapter 12 - Genetic Algorithms."""
from engine import run
from screen_matrix import circle
# pylint: disable=C0103, R0903

WIDTH = 600
HEIGHT = 600
TITLE = "Genetic Algorithms"

class City:
    """An object representing a city location."""

    def __init__(self, x, y, num):
        """Create a City object."""
        self.x = x
        self.y = y
        self.number = num

    def display(self):
        """Draw the City on the window surface."""
        color = (0,255,255)
        circle(self.x, self.y, 10, color, 0)
        screen.draw.text(str(self.number), 
                         center=(self.x, self.y-20),
                         color=color)


def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    screen.fill((0,0,0))
    city_0.display()

city_0 = City(100, 200, 0)

run()
