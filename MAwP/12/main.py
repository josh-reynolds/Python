"""Chapter 12 - Genetic Algorithms."""
from math import dist 
from random import randint, sample
from engine import run, screen
from screen_matrix import circle, polygon
# pylint: disable=C0103, R0903

WIDTH = 600
HEIGHT = 600
TITLE = "Genetic Algorithms"

CITY_COUNT = 10

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

class Route:
    """A series of links between cities."""

    def __init__(self):
        """Create a Route object."""
        self.distance = 0
        self.city_nums = sample(list(range(CITY_COUNT)),
                                CITY_COUNT)

    def display(self):
        """Draw the Route on the window surface."""
        color = (255,0,255)
        points = []
        for j in self.city_nums:
            points.append((cities[j].x, cities[j].y))
        polygon(points, color, 1)
        for j in self.city_nums:
            cities[j].display()

    def calc_length(self):
        self.distance = 0
        for i, num in enumerate(self.city_nums):
            self.distance += dist((cities[num].x, cities[num].y),
                                  (cities[self.city_nums[i-1]].x,
                                   cities[self.city_nums[i-1]].y))
        return self.distance

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    screen.fill((0,0,0))
    r.display()

cities = []
for i in range(CITY_COUNT):
    cities.append(City(randint(50, WIDTH-50),
                       randint(50, HEIGHT-50),
                       i))

r = Route()
print(r.calc_length())

run()
