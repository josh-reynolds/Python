# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

from app import *

class Demo(App):
    def __init__(self):
        super().__init__()

        App.scene = None
        App.scenes =[]

        # tutorial omits adding text to the scene - below is one way to 
        # do it, though more cluttered than the example
        # possibly he is doing this in the Text ctor instead
        # (also, he omits the pos parameter for the Text objects,
        # and handling of the keyword args)

        s1 = Scene(caption='Intro')
        s1.nodes.append(Text('Scene 0', pos=(20,20)))
        s1.nodes.append(Text('Introduction screen', pos=(20,60)))

        s2 = Scene(bg=Color('yellow'), caption='Options')
        s2.bg = Color('yellow')
        s2.nodes.append(Text('Scene 1', pos=(20,20)))
        s2.nodes.append(Text('Option screen', pos=(20,60)))

        s3 = Scene(bg=Color('green'), caption='Main')
        s3.bg = Color('green')
        s3.nodes.append(Text('Scene 2', pos=(20,20)))
        s3.nodes.append(Text('Main screen', pos=(20,60)))

        App.scene = App.scenes[0]

if __name__ == '__main__':
    Demo().run()
