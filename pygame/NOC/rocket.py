from random import uniform, choice, randint, random
from engine import *
from pvector import PVector

class Population:
    def __init__(self, mutation_rate, size, lifetime, max_width, max_height, obstacles, target):
        self.mutation_rate = mutation_rate
        self.population = [Rocket(lifetime, max_width, max_height, obstacles, target) for i in range(size)]
        self.mating_pool = []
        self.generations = 0
        self.lifetime = lifetime

    def live(self):
        for p in self.population:
            p.run()

    def fitness(self):
        for p in self.population:
            p.calculate_fitness()

    def selection(self):
        self.mating_pool = []
        for p in self.population:
            n = int(p.fitness * 100)
            for i in range(n):
                self.mating_pool.append(p)

        if len(self.mating_pool) == 0:
            self.population.sort(key=lambda r: r.fitness)
            for i in range(len(self.population)//2):
                self.mating_pool.append(self.population[i])
            print("zero pool")

        total_fitness = 0
        for r in self.mating_pool:
            total_fitness += r.fitness
        print(f"Average mating pool fitness: {total_fitness/len(self.mating_pool):0.5f}")

    def reproduction(self):
        for i in range(len(self.population)):
            parent_a = choice(self.mating_pool)
            parent_b = choice(self.mating_pool)

            child = parent_a.crossover(parent_b)
            child.mutate(self.mutation_rate)

            self.population[i] = child

    def draw(self):
        for p in self.population:
            p.draw()

class Obstacle:
    def __init__(self, x, y, w, h):
        self.location = PVector(x,y)
        self.width = w
        self.height = h

    def contains(self, v):
        if (v.x > self.location.x and v.x < self.location.x + self.width and
            v.y > self.location.y and v.y < self.location.y + self.height):
            return True
        else:
            return False

    def draw(self):
        screen.draw.rect((self.location.x, self.location.y, self.width, self.height), (0,0,255), 0)

class Rocket:
    def __init__(self, lifetime, max_width, max_height, obstacles, target):
        self.lifetime = lifetime
        self.dna = DNA(lifetime)
        self.fitness = 0
        self.gene_counter = 0

        self.mass = 1
        self.radius = self.mass * 16
        self.location = PVector(max_width//2, max_height)
        self.max_width = max_width
        self.max_height = max_height
        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)

        self.stopped = False
        self.record_distance = 1000
        self.hit_target = False
        self.finish_time = 0

        self.intersection = None

        self.obstacles = obstacles
        self.target = target

    def calculate_fitness(self):
        #f = self.lifetime - self.finish_time + 1/self.record_distance
        d = PVector.dist(self.location, self.target)
        #f = 1/d * 100
        #f = 1/self.record_distance * 100 + self.lifetime - self.finish_time
        f = 1/d * 1000 + self.lifetime - self.finish_time
        #f = f ** 2
        if self.stopped:
            f *= 0.01
        if self.hit_target:
            f *= 2
        if not self.is_onscreen():
            f *= 0.5
        self.line_of_sight()
        if self.intersection is not None:
            f *= 0.1
        self.fitness = f

    def is_onscreen(self):
        return (self.location.x > 0 and
                self.location.x < self.max_width and
                self.location.y > 0 and
                self.location.y < self.max_height)

    def line_of_sight(self):
        # handle obstacle as a line segment
        # find intersection point
        # if point between ends of obstacle segment, return point
        # else no intersection

        # Line AB
        A = (self.location.x, self.location.y)
        B = (self.target.x, self.target.y)
        m1 = (B[1] - A[1])/(B[0] - A[0])   # handle division by zero...
        b1 = A[1] - m1 * A[0]

        # Line CD
        # will generalize to loop over obstacles, but just hard-code first one for now
        C = (self.obstacles[0].location.x, self.obstacles[0].location.y + self.obstacles[0].height/2)
        D = (self.obstacles[0].location.x + self.obstacles[0].width, 
             self.obstacles[0].location.y + self.obstacles[0].height/2)
        m2 = (D[1] - C[1])/(D[0] - C[0])   # handle division by zero...
        b2 = C[1] - m2 * C[0]

        # Intersection
        x = (b2 - b1) / (m1 - m2)   # handle division by zero...
        y = m1 * x + b1

        # limited, does not handle all cases
        if C[0] < x < D[0]:
            self.intersection = (x,y)

    def crossover(self, partner):
        child = Rocket(self.lifetime, self.max_width, self.max_height, self.obstacles, self.target)
        child.dna = self.dna.crossover(partner.dna)
        return child

    def mutate(self, mutation_rate):
        self.dna.mutate(mutation_rate)

    def run(self):
        if not self.stopped:
            self.apply_force(self.dna.genes[self.gene_counter])
            self.gene_counter += 1
            self.gene_counter %= self.lifetime
            self.update()
            self.collision_check()
            self.check_target()

    def check_target(self):
        d = PVector.dist(self.location, self.target)
        if d < self.record_distance:
            self.record_distance = d

        if d < self.radius:
            self.hit_target = True
        else:
            self.finish_time += 1

    def apply_force(self, f):
        self.acceleration + f

    def update(self):
        self.velocity + self.acceleration
        self.location + self.velocity
        self.acceleration * 0

    def collision_check(self):
        for o in self.obstacles:
            if o.contains(self.location):
                self.stopped = True
                self.finish_time = self.lifetime

    def draw(self):
        #screen.draw.line((0,0,0), (self.location.x, self.location.y), (target.x, target.y))
        color = (0,255,0)
        #if self.intersection is not None:
            #screen.draw.circle(self.intersection[0], self.intersection[1], self.radius//4, (255, 0, 255))
            #color = (255,100,100)
        screen.draw.circle(self.location.x, self.location.y, self.radius, color)
        screen.draw.circle(self.location.x, self.location.y, self.radius, (0, 0, 0), 1)

class DNA:
    def __init__(self, lifetime):
        self.max_force = 0.1
        self.genes = []
        for i in range(lifetime):
            vec = PVector.random2D()
            vec * (uniform(0, self.max_force))
            self.genes.append(vec)
        self.lifetime = lifetime

    def crossover(self, partner):
        child = DNA(self.lifetime)
        midpoint = randint(0,len(child.genes))
        for i in range(len(child.genes)):
            if i > midpoint:
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = partner.genes[i]
        return child

    def mutate(self, mutation_rate):
        for i in range(len(self.genes)):
            if random() < mutation_rate:
                vec = PVector.random2D()
                vec * (uniform(0, self.max_force))
                self.genes[i] = vec

