from game import *
from grid import Grid

class Demo(Game):
    def __init__(self):
        super().__init__()

        TitleScreen(caption='Welcome to Nulltima!')

        Overworld(caption='<====!~ NulltimA ~!====>')
        Grid(size=(11, 11), pos=(60, 60))
        PlayerStatusDisplay(pos=(420,60))
        GameStatusDisplay(pos=(420,140))
        Console(pos=(420, 200))

        EndScreen(caption='Game Over')
        Text(text='You are dead.', pos=(200, 60))
        Text(text='Your score is xx.', pos=(200, 80))
        Text(text='Press space to restart,', pos=(200, 100))
        Text(text='or q to quit', pos=(200, 120))

        Game.level = Game.levels[0]
        Game.level.enter()

if __name__ == '__main__':
    Demo().run()
