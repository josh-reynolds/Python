"""Chapter 12 - Genetic Algorithms."""
from math import dist
from random import randint, sample, choice, random
from engine import run, screen
from screen_matrix import circle, polygon
# pylint: disable=C0103, R0903, W0603

WIDTH = 600
HEIGHT = 600
TITLE = "Genetic Algorithms"

CITY_COUNT = 50

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

    def crossover(self, partner):
        """Splice together genes with partner's genes."""
        child = Route()
        index = randint(1, CITY_COUNT-2)
        child.city_nums = self.city_nums[:index]
        if random() < 0.5:
            child.city_nums = child.city_nums[::-1]
        not_slice = [x for x in partner.city_nums if x not in child.city_nums]
        child.city_nums += not_slice
        return child

cities = []
population = []
POP_N = 5000
for i in range(CITY_COUNT):
    cities.append(City(randint(50, WIDTH-50),
                       randint(50, HEIGHT-50),
                       i))
for i in range(POP_N):
    population.append(Route())
best = choice(population)
record_distance = best.calc_length()
first = record_distance

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    global best, record_distance, population
    screen.fill((0,0,0))

    best.display()
    print(record_distance)
    #print(best.city_nums)

    population.sort(key=Route.calc_length)
    population = population[:POP_N]
    length1 = population[0].calc_length()
    if length1 < record_distance:
        record_distance = length1
        best = population[0]

    for j in range(POP_N):
        parent_a, parent_b = sample(population,2)
        child = parent_a.crossover(parent_b)
        population.append(child)

    for j in range(3,25):
        if j < CITY_COUNT:
            new = best.mutate_n(j)
            population.append(new)

    for j in range(3,25):
        if j < CITY_COUNT:
            new = choice(population)
            new = new.mutate_n(j)
            population.append(new)

run()
