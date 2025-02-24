import os
import sys
import pygame
from pygame.locals import *

__version__ = "0.4"

class Actor:

    def __init__(self, image, pos=(0,0), anchor=("center", "center")):
        #print(f"Actor ctor({image}, {pos}, {anchor}) ----- ")
        self._anchor = ("left", "top")
        self._anchor_value = (0,0)
        self.rect = Rect((0,0), (0,0))

        self.image = image
        self.initialize_position(pos, anchor)

    def draw(self):
        #print("draw()  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ")
        screen.blit(self.image_name, self.rect.topleft)

    def collidepoint(self, point):
        #print(f"collidepoint({point})")
        return self.rect.collidepoint(point)

    @property
    def width(self):
        return self.rect.width

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image_name):
        #print(f"set_image({image_name})  ~ ~ ~ ~ ~ ~ ~ ~ ~ ")
        # TO_DO: reconcile with duplication in Screen.blit()
        self.image_name = image_name
        self._image = pygame.image.load('./images/' + image_name + '.png')
        self.update_position()

    def initialize_position(self, pos, anchor):
        #print(f"initialize_position({pos}, {anchor})")
        self._anchor = anchor
        self.calculate_anchor()
        self.pos = pos
    
    def update_position(self):
        #print("update_position()")
        current_position = self.pos
        self.rect.width, self.rect.height = self._image.get_size()
        self.calculate_anchor()
        self.pos = current_position

    @property
    def x(self):
        return self.rect.left + self._anchor_value[0]

    @x.setter
    def x(self, new_x):
        #print(f"set_x({new_x})")
        self.rect.left = new_x - self._anchor_value[0]

    @property
    def y(self):
        return self.rect.top + self._anchor_value[1]

    @y.setter
    def y(self, new_y):
        #print(f"set_y({new_y})")
        self.rect.top = new_y - self._anchor_value[1]

    @property
    def pos(self):
        anchor_x, anchor_y = self._anchor_value

        return (self.rect.topleft[0] + anchor_x, 
                self.rect.topleft[1] + anchor_y)

    @pos.setter
    def pos(self, new_pos):
        #print(f"set_pos({new_pos})")
        anchor_x, anchor_y = self._anchor_value

        self.rect.topleft = (new_pos[0] - anchor_x,
                             new_pos[1] - anchor_y)

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, new_anchor):
        self._anchor = new_anchor
        self.update_position()

    def calculate_anchor(self):
        #print("calculate_anchor()")
        iw = self.image.get_width()
        xs = {"left":0, "center":iw//2, "right":iw}
        ih = self.image.get_height()
        ys = {"top":0, "center":ih//2, "bottom":ih}

        self._anchor_value = (xs[self._anchor[0]], ys[self._anchor[1]])

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
    def __init__(self, width, height):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.surface = pygame.display.set_mode((width, height))
        self.images = {}
        self.draw = Painter(self.surface)

    def fill(self, color):
        self.surface.fill(color)

    # TO_DO: handle other image formats (png/gif/jpg)
    # TO_DO: split image handling for Actors and non-Actors, and shift as needed
    def blit(self, image, position):
        if image not in self.images:
            image_name = './images/' + image + '.png'
            self.images[image] = pygame.image.load(image_name)
        self.surface.blit(self.images[image], position)

class Painter:
    def __init__(self, surface):
        # TO_DO: make this customizeable 
        self.surface = surface
        self.fontname = None
        self.fontsize = 24
        self.fontcolor = Color('black')
        self.set_font()

    def set_font(self):
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    def text(self, text, pos):
        img = self.font.render(text, True, self.fontcolor)
        # TO_DO: address duplication with Screen.blit()
        self.surface.blit(img, pos)

    def line(self, color, start, end):
        pygame.draw.line(self.surface, color, start, end)

class Music:
    def __init__(self):
        pass

    def play(self, song):
        filename = './music/' + song + '.ogg'
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)     # repeat indefinitely

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

class Keyboard:
    def __init__(self):
        self.reset()

    # TO_DO: add support for full set of keys
    def reset(self):
        self.space = False
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.a = False
        self.k = False
        self.m = False
        self.z = False

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise LookupError

class keys:
    SPACE = "space"
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"

class Sounds:
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
screen = Screen(1,1)
music = Music()
keyboard = Keyboard()
sounds = Sounds()

def run():
    #sys.setprofile(trace_function)
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
            # TO_DO: add support for full set of keys
            if event.type == KEYDOWN:
                if event.key == K_q:
                    running = False
                if event.key == K_SPACE:
                    keyboard.space = True
                if event.key == K_UP:
                    keyboard.up = True
                if event.key == K_DOWN:
                    keyboard.down = True
                if event.key == K_LEFT:
                    keyboard.left = True
                if event.key == K_RIGHT:
                    keyboard.right = True
                if event.key == K_a:
                    keyboard.a = True
                if event.key == K_k:
                    keyboard.k = True
                if event.key == K_m:
                    keyboard.m = True
                if event.key == K_z:
                    keyboard.z = True
    
        screen.fill(Color("white"))
        parent.update()
        parent.draw()
        pygame.display.update()
    
    pygame.quit()

def trace_function(frame, event, arg, indent=[0]):
    if event == "call":
        indent[0] += 2
        print("-" * indent[0] + "> call function", frame.f_code.co_qualname)
    elif event == "return":
        print("<" + "-" * indent[0], "exit function", frame.f_code.co_qualname)
        indent[0] -= 2
    return trace_function

