import pygame
from pygame.locals import *

class Level:
    options = {
            'id': 0,
            'bg': Color('gray'),
            'file': '',
            'caption': '',
            }

    def __init__(self, *args, **options):
        Game.levels.append(self)
        Game.level = self

        self.id = Level.options['id']
        Level.options['id'] += 1
        self.nodes = []
        self.bg = Level.options['bg']
        self.file = Level.options['file']
        self.caption = Level.options['caption']

        if options:
            for key,value in options.items():
                self.__dict__[key] = value

        self.rect = Game.screen.get_rect()
        if self.file != '':
            self.img = pygame.image.load(self.file)
            size = Game.screen.get_size()
            self.img = pygame.transform.smoothscale(self.img, size)
        else:
            self.img = pygame.Surface(self.rect.size)
            self.img.fill(self.bg)

        self.enter()

    def draw(self):
        Game.screen.blit(self.img, self.rect)
        for node in self.nodes:
            node.draw()
        pygame.display.flip()

    def enter(self):
        pygame.display.set_caption(self.caption)

    def __str__(self):
        return 'Scene {}'.format(self.id)

class Game:
    level = None
    levels = []

    def __init__(self):
        pygame.init()
        self.flags = RESIZABLE
        self.rect = Rect(0, 0, 640, 480)
        Game.screen = pygame.display.set_mode(self.rect.size, self.flags)
        Game.running = True
        self.shortcuts = {
                (K_LEFT, 0): '',
                (K_RIGHT, 0): '',
                (K_UP, 0): '',
                (K_DOWN, 0): '',
                (K_q, 0): 'Game.running = False',
                }

    def run(self):
        while Game.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    Game.running = False
                if event.type == KEYDOWN:
                    self.do_shortcut(event)

            Game.screen.fill(Color('gray'))
            Game.level.draw()
            pygame.display.update()

        pygame.quit()

    def do_shortcut(self, event):
        k = event.key
        m = event.mod
        if (k, m) in self.shortcuts:
            exec(self.shortcuts[k, m])


if __name__ == "__main__":
    g = Game()
    Level()
    g.run()
