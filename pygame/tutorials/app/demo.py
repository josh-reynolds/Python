# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

from app import *

class Demo(App):
    def __init__(self):
        super().__init__()

        Scene(file='./bg_1.png', caption='Intro')
        Text('Scene 0', pos=(20,20), fontcolor=Color('white'))
        Text('Introduction screen', pos=(20,60), fontcolor=Color('white'))

        Scene(file='./bg_2.png', bg=Color('yellow'), caption='Options')
        Text('Scene 1', pos=(20,20), fontcolor=Color('blue'))
        Text('Option screen', pos=(20,60), fontcolor=Color('blue'))

        Scene(bg=Color('green'), caption='Main')
        Text('Scene 2', pos=(20,20))
        Text('Main screen', pos=(20,60))

        App.scene = App.scenes[0]

if __name__ == '__main__':
    Demo().run()
