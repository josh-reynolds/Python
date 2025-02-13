import os
import sys
import pygame
from pygame.locals import *

__version__ = "0.2"

class Actor:
    def __init__(self, image, pos, anchor=("center", "center")):
        self.image_name = image
        # TO_DO: reconcile with duplication in Screen.blit()
        self.image = pygame.image.load('./images/' + image + '.png')
        self.rect = self.image.get_rect()

        self.anchor = anchor
        self.pos = pos

    def draw(self):
        screen.blit(self.image_name, self.pos)

    def collidepoint(self, point):
        return self.rect.collidepoint(point)

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, new_x):
        self.rect.x = new_x

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, new_y):
        self.rect.y = new_y

    @property
    def pos(self):
        return (self.rect.x, self.rect.y)

    @pos.setter
    def pos(self, new_pos):
        if self.anchor[0] == "left":
            self.rect.x = new_pos[0]
        if self.anchor[0] == "center":
            self.rect.x = new_pos[0] - self.rect.width//2
        if self.anchor[0] == "right":
            self.rect.x = new_pos[0] - self.rect.width

        if self.anchor[1] == "top":
            self.rect.y = new_pos[1]
        if self.anchor[1] == "center":
            self.rect.y = new_pos[1] - self.rect.height//2
        if self.anchor[1] == "bottom":
            self.rect.y = new_pos[1] - self.rect.height

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
        self.display = pygame.display.set_mode((width, height))
        self.images = {}

    def fill(self, color):
        self.display.fill(color)

    # TO_DO: handle other image formats (png/gif/jpg)
    # TO_DO: split image handling for Actors and non-Actors, and shift as needed
    def blit(self, image, position):
        if image not in self.images:
            image_name = './images/' + image + '.png'
            self.images[image] = pygame.image.load(image_name)
        self.display.blit(self.images[image], position)

    def draw_line(self, color, start, end):
        pygame.draw.line(self.display, color, start, end)

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
    parent = sys.modules['__main__']
    parent.screen = Screen(parent.WIDTH, parent.HEIGHT)
    pygame.display.set_caption(parent.TITLE)
    pygame.key.set_repeat(50,50)
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
    
