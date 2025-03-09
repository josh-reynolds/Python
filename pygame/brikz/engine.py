"""A simple wrapper around Pygame to handle boilerplate code, based on Pygame Zero.

This module contains the following:

    Actor - class to handle moving graphical objects.
    Screen - wraps the Pygame screen surface.
    Painter - methods to draw on the screen.
    Music - wraps the Pygame music mixer.
    Keyboard - holds flags indicating keyboard state.
    Sounds - wraps the Pygame audio mixer.

    screen - singleton instance of Screen for use by game scripts.
    music - singleton instance of Music for use by game scripts.
    keyboard - singleton instance of Keyboard for use by game scripts.
    keys - contains all keyboard key name constants.
    sounds - singleton instance of Sounds for use by game scripts.

    run() - entry point containing the core game loop.

Game scripts should generally import the singleton entries, run(), and Actor. The 
game loop will expect to find update(), draw(), and the constants WIDTH, HEIGHT, and
TITLE defined in the game script. Invoking run() at the end of the script will start the
game in motion, invoking the user-defined update() and run() once per frame, and
flagging keyboard events in the keyboard object as they occur. The engine will look for
images and sound files in the subdirectories ./images, ./sounds and ./music.
"""

__all__ = ['Actor', 'screen', 'music', 'keyboard', 'keys', 'sounds', 'run']
__version__ = "1.1"

import os
import sys
import pygame
from pygame.locals import *

DEBUG_ACTOR = False

# TO_DO: handle files w/ same name but different extensions
def _load_image(image_name):
    """Internal function to handle loading image files in png, jpg or gif formats."""

    img = None
    for entry in os.listdir('./images/'):
        name,extension = entry.split('.')
        if name == image_name and (extension == 'png' or
                                   extension == 'jpg' or
                                   extension == 'gif'):

            try:
                img = pygame.image.load('./images/' + image_name + '.' + extension)
            except FileNotFoundError:
                pass

    if not img:
        print(f"{image_name} not found in ./images or is not an image file.")
        sys.exit()
    else:
        return img


class Actor:
    """Actor - class to handle moving graphical objects."""

    def __init__(self, image, pos=(0,0), anchor=("center", "center")):
        if DEBUG_ACTOR: print(f"Actor ctor({image}, {pos}, {anchor}) ----- ")
        
        self._anchor = ("left", "top")
        self._anchor_value = (0,0)
        self.rect = Rect((0,0), (0,0))

        if anchor == None:
            anchor = ("center","center")

        self.image = image
        self.initialize_position(pos, anchor)

    def draw(self):
        if DEBUG_ACTOR: print("draw()  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ")

        screen.blit(self.image, self.rect.topleft)

    def collidepoint(self, point):
        if DEBUG_ACTOR: print(f"collidepoint({point})")

        return self.rect.collidepoint(point)

    @property
    def width(self):
        return self.rect.width

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image_name):
        if DEBUG_ACTOR: print(f"set_image({image_name})  ~ ~ ~ ~ ~ ~ ~ ~ ~ ")
        
        self.image_name = image_name
        self._image = _load_image(image_name)
        self.update_position()

    def initialize_position(self, pos, anchor):
        if DEBUG_ACTOR: print(f"initialize_position({pos}, {anchor})")

        self._anchor = anchor
        self.calculate_anchor()
        self.pos = pos
    
    def update_position(self):
        if DEBUG_ACTOR: print("update_position()")

        current_position = self.pos
        self.rect.width, self.rect.height = self._image.get_size()
        self.calculate_anchor()
        self.pos = current_position

    @property
    def x(self):
        return self.rect.left + self._anchor_value[0]

    @x.setter
    def x(self, new_x):
        if DEBUG_ACTOR: print(f"set_x({new_x})")

        self.rect.left = new_x - self._anchor_value[0]

    @property
    def y(self):
        return self.rect.top + self._anchor_value[1]

    @y.setter
    def y(self, new_y):
        if DEBUG_ACTOR: print(f"set_y({new_y})")

        self.rect.top = new_y - self._anchor_value[1]

    @property
    def pos(self):
        anchor_x, anchor_y = self._anchor_value

        return (self.rect.topleft[0] + anchor_x, 
                self.rect.topleft[1] + anchor_y)

    @pos.setter
    def pos(self, new_pos):
        if DEBUG_ACTOR: print(f"set_pos({new_pos})")

        anchor_x, anchor_y = self._anchor_value

        self.rect.topleft = (new_pos[0] - anchor_x,
                             new_pos[1] - anchor_y)

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, new_anchor):
        if DEBUG_ACTOR: print(f"set_anchor({new_anchor})")

        self._anchor = new_anchor
        self.update_position()

    def calculate_anchor(self):
        if DEBUG_ACTOR: print("calculate_anchor()")

        iw = self.image.get_width()
        xs = {"left":0, "center":iw//2, "right":iw}
        ih = self.image.get_height()
        ys = {"top":0, "center":ih//2, "bottom":ih}

        if str(self._anchor[0]).isnumeric():
            new_x = self._anchor[0]
        else:
            new_x = xs[self._anchor[0]]

        if str(self._anchor[1]).isnumeric():
            new_y = self._anchor[1]
        else:
            new_y = ys[self._anchor[1]]

        self._anchor_value = (new_x, new_y)

    @property
    def top(self):
        return self.rect.top

    @property
    def bottom(self):
        return self.rect.bottom

    @property
    def center(self):
        return self.rect.center

class Screen:
    """Screen - wraps the Pygame screen surface."""

    def __init__(self, width, height):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.surface = pygame.display.set_mode((width, height))
        self.images = {}
        self.draw = Painter(self.surface)

    def fill(self, color):
        self.surface.fill(color)

    def blit(self, image, position):
        if isinstance(image, pygame.Surface):
            surf = image
        elif isinstance(image, str):
            if image not in self.images:
                self.images[image] = _load_image(image)
            surf = self.images[image]

        self.surface.blit(surf, position)


class Painter:
    """Painter - methods to draw on the screen.

    These methods are exposed via Screen.draw, and should not be directly invoked.
    """

    def __init__(self, surface):
        # TO_DO: make this customizeable 
        self.surface = surface
        self.fontname = None
        self.fontsize = 24
        self.fontcolor = Color('black')
        self.set_font()

    def set_font(self):
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    #TO_DO: only partial positioning implemented thus far, and a bit creaky
    # this is 'borrowed' from ptext, which is what Pygame Zero uses internally
    def text(self, text, pos=None, center=None):
        if center and not pos:
            x, y = center
            hanchor, vanchor = 0.5, 0.5
        elif pos and not center:
            x, y = pos
            hanchor, vanchor = 0, 0
        else:
            raise Exception("Must specify either pos or center location")

        img = self.font.render(text, True, self.fontcolor)

        x -= hanchor * img.get_width()
        y -= vanchor * img.get_height()

        x = int(round(x))
        y = int(round(y))

        # TO_DO: address duplication with Screen.blit()
        self.surface.blit(img, (x,y))

    def line(self, color, start, end):
        pygame.draw.line(self.surface, color, start, end)


class Music:
    """Music - wraps the Pygame music mixer."""
    
    def __init__(self):
        pass

    def play(self, song):
        filename = './music/' + song + '.ogg'
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)     # repeat indefinitely

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def fadeout(self, time):
        pygame.mixer.music.fadeout(time)


class Keyboard:
    """Keyboard - holds flags indicating keyboard state."""

    def __init__(self):
        self.reset()

    def reset(self):
        for i in dir(self):
            if not i.startswith('__') and i != 'reset':
                setattr(self, i, False)

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)


class keys:
    """keys - contains all keyboard key name constants."""
    pass


class Sounds:
    """Sounds - wraps the Pygame audio mixer."""

    def __init__(self):
        files = []
        for entry in os.listdir('./sounds/'):
            if os.path.isfile('./sounds/' + entry):
                name, extension = entry.split('.')
                if extension == 'ogg' or extension == 'wav':
                    files.append((name,extension))

        for file in files:
            filename = './sounds/' + file[0] + '.' + file[1]
            setattr(self, file[0], pygame.mixer.Sound(filename))


pygame.init()

"""screen - singleton instance of Screen for use by game scripts."""
screen = Screen(1,1)

"""music - singleton instance of Music for use by game scripts."""
music = Music()

"""keyboard - singleton instance of Keyboard for use by game scripts."""
keyboard = Keyboard()

"""sounds - singleton instance of Sounds for use by game scripts."""
sounds = Sounds()

# extract all key name constants imported from pygame.locals
# and expose via fields on keys
_key_constants = [i for i in dir() if i.startswith('K_')]
for i in _key_constants:
    const = i[2:].upper()     # remove the initial 'K_'
    setattr(keys, const, const.lower())
    setattr(keyboard, const.lower(), False)

def run():
    """run() - entry point containing the core game loop."""

    #sys.setprofile(_trace_function)
    parent = sys.modules['__main__']
    parent.screen = Screen(parent.WIDTH, parent.HEIGHT)
    pygame.display.set_caption(parent.TITLE)
    pygame.key.set_repeat(10,10)

    #screen.fill(Color("white"))
    #parent.once()

    running = True
    while running:
        pygame.time.Clock().tick(60)
        keyboard.reset()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_q:
                    running = False

                name = pygame.key.name(event.key)
                if name.startswith('left') and len(name) > 4:
                    name = 'l' + name[5:]
                if name.startswith('right') and len(name) > 5:
                    name = 'r' + name[6:]

                if hasattr(keys, name.upper()):
                    setattr(keyboard, name, True)
    
        screen.fill(Color("white"))
        parent.update()
        parent.draw()
        pygame.display.update()
    
    pygame.quit()

def _trace_function(frame, event, arg, indent=[0]):
    """Internal function to display function entry/exit while debugging."""

    if event == "call":
        indent[0] += 2
        print("-" * indent[0] + "> call function", frame.f_code.co_qualname)
    elif event == "return":
        print("<" + "-" * indent[0], "exit function", frame.f_code.co_qualname)
        indent[0] -= 2
    return _trace_function

