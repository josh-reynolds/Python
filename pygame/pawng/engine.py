import os
import pygame
from pygame.locals import *

class Actor:
    def __init__(self, image, pos):
        self.image = image
        self.x = pos[0]
        self.y = pos[1]

    def draw(self):
        screen.blit(self.image, (self.x, self.y), center=True)

    @property
    def pos(self):
        return (self.x, self.y)

class Screen:
    def __init__(self, width, height):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.display = pygame.display.set_mode((width, height))
        self.images = {}

    def fill(self, color):
        self.display.fill(color)

    # TO_DO: handle other image formats (png/gif/jpg)
    def blit(self, image, position, center=False):
        if image not in self.images:
            image_name = './images/' + image + '.png'
            self.images[image] = pygame.image.load(image_name)
        if center:
            c = self.images[image].get_rect().center
            position = (position[0] - c[0], position[1] - c[1])
        self.display.blit(self.images[image], position)

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
        self.a = False
        self.k = False
        self.m = False
        self.z = False

# TO_DO: hardcoded to Pawng sound effect files - make ths dynamic
#        also add support for wav files
class Sounds:
    def __init__(self):
        self.bounce0 = pygame.mixer.Sound('./sounds/bounce0.ogg')
        self.bounce1 = pygame.mixer.Sound('./sounds/bounce1.ogg')
        self.bounce2 = pygame.mixer.Sound('./sounds/bounce2.ogg')
        self.bounce3 = pygame.mixer.Sound('./sounds/bounce3.ogg')
        self.bounce4 = pygame.mixer.Sound('./sounds/bounce4.ogg')
        self.bounce_synth0 = pygame.mixer.Sound('./sounds/bounce_synth0.ogg')
        self.down = pygame.mixer.Sound('./sounds/down.ogg')
        self.hit0 = pygame.mixer.Sound('./sounds/hit0.ogg')
        self.hit1 = pygame.mixer.Sound('./sounds/hit1.ogg')
        self.hit2 = pygame.mixer.Sound('./sounds/hit2.ogg')
        self.hit3 = pygame.mixer.Sound('./sounds/hit3.ogg')
        self.hit4 = pygame.mixer.Sound('./sounds/hit4.ogg')
        self.hit_fast0 = pygame.mixer.Sound('./sounds/hit_fast0.ogg')
        self.hit_medium0 = pygame.mixer.Sound('./sounds/hit_medium0.ogg')
        self.hit_slow0 = pygame.mixer.Sound('./sounds/hit_slow0.ogg')
        self.hit_synth0 = pygame.mixer.Sound('./sounds/hit_synth0.ogg')
        self.hit_veryfast0 = pygame.mixer.Sound('./sounds/hit_veryfast0.ogg')
        self.score_goal0 = pygame.mixer.Sound('./sounds/score_goal0.ogg')
        self.up = pygame.mixer.Sound('./sounds/up.ogg')

pygame.init()
screen = Screen(1,1)
music = Music()
keyboard = Keyboard()
sounds = Sounds()

def run(width, height, title, update_func, draw_func):
    update = update_func
    draw = draw_func
    screen = Screen(width, height)
    pygame.display.set_caption(title)
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
                if event.key == K_SPACE:
                    keyboard.space = True
                if event.key == K_UP:
                    keyboard.up = True
                if event.key == K_DOWN:
                    keyboard.down = True
                if event.key == K_a:
                    keyboard.a = True
                if event.key == K_k:
                    keyboard.k = True
                if event.key == K_m:
                    keyboard.m = True
                if event.key == K_z:
                    keyboard.z = True
    
        screen.fill(Color("white"))
        update()
        draw()
        pygame.display.update()
    
    pygame.quit()
    
