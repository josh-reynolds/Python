"""Chapter 12 - Genetic Algorithms."""
from math import dist
from random import randint, sample
from engine import run, screen
from screen_matrix import circle, polygon
# pylint: disable=C0103, R0903, W0603

WIDTH = 600
HEIGHT = 600
TITLE = "Genetic Algorithms"

CITY_COUNT = 10

random_improvements = 0
mutated_improvements = 0

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
        """Calculate the length of the Route."""
        self.distance = 0
        for j, num in enumerate(self.city_nums):
            self.distance += dist((cities[num].x, cities[num].y),
                                  (cities[self.city_nums[j-1]].x,
                                   cities[self.city_nums[j-1]].y))
        return self.distance

    def mutate_n(self, num):
        """Mutate a Route by swapping num cities."""
        indices = sample(list(range(CITY_COUNT)), num)
        child = Route()
        child.city_nums = self.city_nums[::]
        for j in range(num-1):
            child.city_nums[indices[j]],\
                    child.city_nums[indices[(j+1)%num]] = \
                    child.city_nums[indices[(j+1)%num]],\
                    child.city_nums[indices[j]]
        return child

cities = []
for i in range(CITY_COUNT):
    cities.append(City(randint(50, WIDTH-50),
                       randint(50, HEIGHT-50),
                       i))
best = Route()
record_distance = best.calc_length()

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    global best, record_distance, random_improvements
    global mutated_improvements
    screen.fill((0,0,0))

    best.display()
    print(record_distance)
    print(f"random: {random_improvements}")
    print(f"mutated: {mutated_improvements}")

    r = Route()
    l1 = r.calc_length()
    if l1 < record_distance:
        record_distance = l1
        best = r
        random_improvements += 1

    for i in range(2,6):
        mutated = Route()
        mutated.city_nums = best.city_nums
        mutated = mutated.mutate_n(i)
        l2 = mutated.calc_length()
        if l2 < record_distance:
            record_distance = l2
            best = mutated
            mutated_improvements += 1


run()
