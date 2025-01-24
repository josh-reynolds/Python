import random
import pygame
from pygame.locals import *
from monsters import monster

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

class StatusDisplay:
    def __init__(self, pos):
        self.pos = pos
        Game.level.nodes.append(self)
        self.fontname = None
        self.fontsize = 24
        self.fontcolor = Color('black')
        self.set_font()
        self.render()

    def set_font(self):
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    def render(self):
        self.width = 200

        moves = str(Game.moves)
        coordinate = str(Game.level.grid.to_world(Game.level.grid.center))
        contents = ["moves: " + moves, 
                    "coordinates: " + coordinate]
        maxlines = len(contents) + 1

        self.img = pygame.Surface((self.width, 20 + maxlines * self.fontsize))
        self.img.fill(Color('white'))
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

        for i,line in enumerate(contents):
            text = self.font.render(line, True, self.fontcolor)
            self.img.blit(text, (10, 10 + i * self.fontsize))

    def draw(self):
        self.render()
        Game.screen.blit(self.img, self.rect)

    def update(self):
        pass

class Console:
    def __init__(self, pos):
        self.pos = pos
        Game.level.nodes.append(self)
        Game.level.console = self
        self.fontname = None
        self.fontsize = 24
        self.fontcolor = Color('black')
        self.set_font()
        self.lines = []
        self.maxlines = 5
        self.prompt = '|>  '
        self.add()
        self.render()

    def set_font(self):
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    def render(self):
        self.width = 200
        self.img = pygame.Surface((self.width, 20 + self.maxlines * self.fontsize))
        self.img.fill(Color('cadetblue3'))
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

        for i,line in enumerate(self.lines):
            text = self.font.render(line, True, self.fontcolor)
            self.img.blit(text, (10, 10 + i * self.fontsize))

    def add(self, text=None):
        if self.lines:
            self.lines.pop()
        if text:
            self.lines.append(self.prompt + text)
        self.lines.append(self.prompt)

    def draw(self):
        self.render()
        Game.screen.blit(self.img, self.rect)

    def update(self):
        if len(self.lines) > self.maxlines:
            self.lines.pop(0)

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
        self.last_move = ''
        self.console = None
        self.monsters = []
        self.shortcuts = {
                (K_LEFT, 0): ('self.grid.move(-1,0)', 'West'),
                (K_RIGHT, 0): ('self.grid.move(1,0)', 'East'),
                (K_UP, 0): ('self.grid.move(0,-1)', 'North'),
                (K_DOWN, 0): ('self.grid.move(0,1)', 'South'),
                (K_SPACE, 0): ('self.grid.no_action()', 'Pass'),
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
        for monster in self.monsters:
            monster.update()

    def draw(self):
        Game.screen.blit(self.img, self.rect)
        for node in self.nodes:
            node.draw()

        for monster in self.monsters:
            monster.draw()

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
            action = self.shortcuts[k,m]
            exec(action[0])
            self.last_move = action[1]

    def check_move(self):
        if self.moved:
            self.moved = False
            self.spawn()
            for monster in self.monsters:
                monster.think()
            if self.console:
                self.console.add(self.last_move)
            return True
        return False

    def spawn(self):
        if random.random() < 0.1:
            grid_coordinate = random.choice(self.grid.spawnable())
            world_coordinate = self.grid.to_world(grid_coordinate)
            self.monsters.append(monster(world_coordinate, self))

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

class ScreenMock():
    def get_rect(self):
        return pygame.Rect(0,0,100,100)

class GameMock(Game):
    def __init__(self):
        Game.screen = ScreenMock()

if __name__ == "__main__":
    g = Game()
    Level()
    g.run()
