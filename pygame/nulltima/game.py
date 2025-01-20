import random
import pygame
from pygame.locals import *

class Text:
    def __init__(self, text, pos, **options):
        self.text = text
        self.pos = pos

        Game.level.nodes.append(self)

        self.fontname = None
        self.fontsize = 24
        self.fontcolor = Color('black')

        if options:
            for key,value in options.items():
                self.__dict__[key] = value

        self.set_font()
        self.render()

    def set_font(self):
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    def render(self):
        self.img = self.font.render(self.text, True, self.fontcolor)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

    def update(self):
        pass

    def draw(self):
        Game.screen.blit(self.img, self.rect)

class Status(Text):
    def __init__(self, pos):
        super().__init__('moves: ', pos)

    def update(self):
        self.text = 'moves: ' + str(Game.moves)

    def draw(self):
        self.render()
        Game.screen.blit(self.img, self.rect)

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
        self.moved = False
        self.monsters = []
        self.shortcuts = {
                (K_LEFT, 0): 'self.grid.move(-1,0)',
                (K_RIGHT, 0): 'self.grid.move(1,0)',
                (K_UP, 0): 'self.grid.move(0,-1)',
                (K_DOWN, 0): 'self.grid.move(0,1)',
                }

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

    def update(self):
        for node in self.nodes:
            node.update()

    def draw(self):
        Game.screen.blit(self.img, self.rect)
        for node in self.nodes:
            node.draw()
        pygame.display.flip()

    def enter(self):
        pygame.display.set_caption(self.caption)

    def do_event(self, event):
        if event.type == KEYDOWN:
            self.do_shortcut(event)
            self.moved = True

    def do_shortcut(self, event):
        k = event.key
        m = event.mod
        if (k, m) in self.shortcuts:
            exec(self.shortcuts[k, m])

    def check_move(self):
        if self.moved:
            self.moved = False
            self.spawn()
            return True
        return False

    def spawn(self):
        if random.random() < 0.1:
            self.monsters.append((random.randint(0,self.grid.width-1) + self.grid.offset[0],
                                  random.randint(0,self.grid.height-1) + self.grid.offset[1]))
            print("Spawning monster!")
            print(self.monsters)

    def __str__(self):
        return 'Scene {}'.format(self.id)

class Game:
    level = None
    levels = []
    screen = None
    moves = 0

    def __init__(self):
        pygame.init()
        self.flags = RESIZABLE
        self.rect = Rect(0, 0, 640, 480)
        Game.screen = pygame.display.set_mode(self.rect.size, self.flags)
        Game.running = True
        self.shortcuts = {
                (K_q, 0): 'Game.running = False',
                }

    def run(self):
        while Game.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    Game.running = False
                if event.type == KEYDOWN:
                    self.do_shortcut(event)

                Game.level.do_event(event)
                if Game.level.check_move():
                    Game.moves += 1

            Game.level.update()

            Game.screen.fill(Color('gray'))
            Game.level.draw()
            pygame.display.update()

        pygame.quit()

    def do_shortcut(self, event):
        k = event.key
        m = event.mod
        if (k, m) in self.shortcuts:
            exec(self.shortcuts[k, m])

    def get_moves():
        return Game.moves

if __name__ == "__main__":
    g = Game()
    Level()
    g.run()
