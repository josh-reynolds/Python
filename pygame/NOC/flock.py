from random import randint
from boids import Boid

class Flock:
    def __init__(self, max_width, max_height, resolution, boid_count):
        self.grid = [[[] for i in range(max_width//resolution)] for i in range(max_height//resolution)]
        self.max_width = len(self.grid[0])-1
        self.max_height = len(self.grid)-1
        self.resolution = resolution

        self.boids = []
        for i in range(boid_count):
            self.add_boid(Boid(max_width//2 + randint(-1,1), max_height//2 + randint(-1,1), max_width, max_height))

    def run(self):
        for b in self.boids:
            prev_column = int(b.location.y) // self.resolution
            prev_column = max(0, min(prev_column, self.max_height))
            prev_row = int(b.location.x) // self.resolution
            prev_row = max(0, min(prev_row, self.max_width))
            if b not in self.grid[prev_column][prev_row]:
                self.grid[prev_column][prev_row].append(b)

            b.flock(self.grid[prev_column][prev_row])
            b.update()

            new_column = int(b.location.y) // self.resolution
            new_column = max(0, min(new_column, self.max_height))
            new_row = int(b.location.x) // self.resolution
            new_row = max(0, min(new_row, self.max_width))
            if new_column != prev_column or new_row != prev_row:
                if b not in self.grid[new_column][new_row]:
                    self.grid[new_column][new_row].append(b)
                self.grid[prev_column][prev_row].remove(b)

    def add_boid(self, boid):
        self.boids.append(boid)

    def draw(self):
        for b in self.boids:
            b.draw()
