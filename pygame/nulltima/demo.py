from game import *
from grid import Grid

class Demo(Game):
    def __init__(self):
        super().__init__()

        Level(caption='<====!~ NulltimA ~!====>')
        Grid(size=(11, 11), pos=(60, 60))
        Text(text='Arrow keys to move', pos=(420, 60))
        Text(text='q to quit', pos=(420, 80))
        PlayerStatusDisplay(pos=(420,100))
        StatusDisplay(pos=(420,160))
        Console(pos=(420, 220))

if __name__ == '__main__':
    Demo().run()
