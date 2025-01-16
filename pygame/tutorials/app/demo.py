# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

from app import *

class Demo(App):
    def __init__(self):
        super().__init__()

        App.scene = None
        App.scenes =[]

        Scene(caption='Intro')
        Text('Scene 0', pos=(20,20))
        Text('Introduction screen', pos=(20,60))

        Scene(bg=Color('yellow'), caption='Options')
        Text('Scene 1', pos=(20,20))
        Text('Option screen', pos=(20,60))

        Scene(bg=Color('green'), caption='Main')
        Text('Scene 2', pos=(20,20))
        Text('Main screen', pos=(20,60))

        App.scene = App.scenes[0]

if __name__ == '__main__':
    Demo().run()
