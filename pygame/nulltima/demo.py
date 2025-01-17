from game import *
from grid import grid

class Demo(Game):
    def __init__(self):
        super().__init__()

        Level()
        g = grid(11, 11, 60, 60, 32, 32)
        g.world.open_file("large_world.txt")

        self.level.nodes.append(g)

if __name__ == '__main__':
    Demo().run()
