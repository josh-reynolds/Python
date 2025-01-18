from game import *
from grid import grid

class Demo(Game):
    def __init__(self):
        super().__init__()

        Level(caption="<====!~ NulltimA ~!====>")

        g = grid(11, 11, 60, 60, 32, 32)
        g.world.open_file("large_world.txt")
        self.level.nodes.append(g)

        Text('Arrow keys to move', pos=(420, 60))
        Text('q to quit', pos=(420, 80))

if __name__ == '__main__':
    Demo().run()
