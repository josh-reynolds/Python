# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

from app import *

class Demo(App):
    def __init__(self):
        super().__init__()

        App.scene = None
        App.scenes =[]

        # (also, he omits the pos parameter for the Text objects,
        # and handling of the keyword args)

        Scene(caption='Intro')
        Text('Scene 0', pos=(20,20))
        Text('Introduction screen', pos=(20,60))

        Scene(bg=Color('yellow'), caption='Options')
        #Color('yellow')
        Text('Scene 1', pos=(20,20))
        Text('Option screen', pos=(20,60))

        Scene(bg=Color('green'), caption='Main')
        #Color('green')
        Text('Scene 2', pos=(20,20))
        Text('Main screen', pos=(20,60))

        App.scene = App.scenes[0]

if __name__ == '__main__':
    Demo().run()
