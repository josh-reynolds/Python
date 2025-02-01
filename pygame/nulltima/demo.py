from game import *
from grid import Grid

class Demo(Game):
    def __init__(self):
        super().__init__()

        Level(caption='<====!~ NulltimA ~!====>')
        Grid(size=(11, 11), pos=(60, 60))
        Text(text='Arrow keys to move,', pos=(420, 60))
        Text(text='q to quit', pos=(420, 80))
        PlayerStatusDisplay(pos=(420,100))
        GameStatusDisplay(pos=(420,180))
        Console(pos=(420, 240))

        EndScreen(caption='Game Over')
        Text(text='You are dead.', pos=(200, 60))
        Text(text='Your score is xx.', pos=(200, 80))
        Text(text='Press space to restart,', pos=(200, 100))
        Text(text='or q to quit', pos=(200, 120))

        Game.level = Game.levels[0]

if __name__ == '__main__':
    Demo().run()
