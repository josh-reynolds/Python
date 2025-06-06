

class Flock:
    def __init__(self, grid, max_width, max_height, resolution):
        self.boids = []
        self.grid = grid
        self.max_width = max_width
        self.max_height = max_height
        self.resolution = resolution

    def run(self):
        for b in self.boids:
            prev_column = int(b.location.y) // self.resolution
            prev_column = max(0, min(prev_column, self.max_height//self.resolution-1))
            prev_row = int(b.location.x) // self.resolution
            prev_row = max(0, min(prev_row, self.max_width//self.resolution-1))
            if b not in self.grid[prev_column][prev_row]:
                self.grid[prev_column][prev_row].append(b)

            b.flock(self.grid[prev_column][prev_row])
            b.update()

            new_column = int(b.location.y) // self.resolution
            new_column = max(0, min(new_column, self.max_height//self.resolution-1))
            new_row = int(b.location.x) // self.resolution
            new_row = max(0, min(new_row, self.max_width//self.resolution-1))
            if new_column != prev_column or new_row != prev_row:
                if b not in self.grid[new_column][new_row]:
                    self.grid[new_column][new_row].append(b)
                self.grid[prev_column][prev_row].remove(b)

    def add_boid(self, boid):
        self.boids.append(boid)

    def draw(self):
        for b in self.boids:
            b.draw()
