from game import *
from grid import Grid

class Demo(Game):
    def __init__(self):
        super().__init__()

        Level(caption="<====!~ NulltimA ~!====>")
        Grid(11, 11, 60, 60)
        Text('Arrow keys to move', pos=(420, 60))
        Text('q to quit', pos=(420, 80))
        Text('---------', pos=(420, 100))
        Status(pos=(420, 120))

if __name__ == '__main__':
    Demo().run()
