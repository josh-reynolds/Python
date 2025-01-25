import random
import pygame
from pygame.locals import *
import monsters
import player

class Component:
    def __init__(self, pos):
        self.pos = pos
        self.fontname = None
        self.fontsize = 24
        self.fontcolor = Color('white')
        self.set_font()
        Game.level.components.append(self)

    def set_font(self):
        self.font = pygame.font.Font(self.fontname, self.fontsize)
        
class Text(Component):
    def __init__(self, text, pos, **options):
        super().__init__(pos)
        self.text = text

        if options:
            for key,value in options.items():
                self.__dict__[key] = value

        self.render()

    def render(self):
        self.img = self.font.render(self.text, True, self.fontcolor)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

    def update(self):
        pass

    def draw(self):
        Game.screen.blit(self.img, self.rect)

class StatusDisplay(Component):
    def __init__(self, pos):
        super().__init__(pos)
        self.bg = Color('gray33')
        self.render()

    def render(self):
        self.width = 200

        moves = str(Game.moves)
        coordinate = str(Game.level.grid.to_world(Game.level.grid.center))
        contents = ["moves: " + moves, 
                    "coordinates: " + coordinate]
        maxlines = len(contents) + 1

        self.img = pygame.Surface((self.width, 20 + maxlines * self.fontsize))
        self.img.fill(self.bg)
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

class Console(Component):
    def __init__(self, pos):
        super().__init__(pos)
        Game.level.console = self
        self.bg = Color('gray50')
        self.lines = []
        self.maxlines = 5
        self.prompt = '|>  '
        self.prompt_pos = 0
        self.prompt_color = self.bg
        self.time = 0
        self.add()
        self.render()

    def render(self):
        self.width = 200
        self.img = pygame.Surface((self.width, 20 + self.maxlines * self.fontsize))
        self.img.fill(self.bg)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos
        self.prompt_pos = (len(self.lines) - 1) * self.fontsize + 5

        for i,line in enumerate(self.lines):
            text = self.font.render(line, True, self.fontcolor)
            self.img.blit(text, (10, 10 + i * self.fontsize))

    def add(self, text=None):
        if self.lines:
            self.lines.pop()                  # remove the empty prompt line
        if text:
            self.lines.append(self.prompt + text)
        self.lines.append(self.prompt)        # and put it back again...

    def draw(self):
        self.render()
        cursor_rect = (30, self.prompt_pos, self.fontsize/6, self.fontsize)
        pygame.draw.rect(self.img, self.prompt_color, cursor_rect)
        Game.screen.blit(self.img, self.rect)

    def update(self):
        if len(self.lines) > self.maxlines:
            self.lines.pop(0)
        self.time += 1
        if self.time > 10:
            self.time = 0
            if self.prompt_color == self.bg:
                self.prompt_color = self.fontcolor
            else:
                self.prompt_color = self.bg

class Level:
    options = {
            'id': 0,
            'bg': Color('black'),
            'file': '',
            'caption': '',
            }

    def __init__(self, *args, **options):
        Game.levels.append(self)
        Game.level = self

        self.id = Level.options['id']
        Level.options['id'] += 1
        self.components = []
        self.bg = Level.options['bg']
        self.file = Level.options['file']
        self.caption = Level.options['caption']
        self.moved = False
        self.last_move = ''
        self.console = None
        self.monsters = []
        self.player = player.Player((15,15), self)
        self.shortcuts = {
                (K_LEFT, 0): ('self.player.move(-1,0)', 'West'),
                (K_RIGHT, 0): ('self.player.move(1,0)', 'East'),
                (K_UP, 0): ('self.player.move(0,-1)', 'North'),
                (K_DOWN, 0): ('self.player.move(0,1)', 'South'),
                (K_SPACE, 0): ('self.player.no_action()', 'Pass'),
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
        for component in self.components:
            component.update()
        for monster in self.monsters:
            monster.update()
        self.player.update()

    def draw(self):
        Game.screen.blit(self.img, self.rect)
        for component in self.components:
            component.draw()
        for monster in self.monsters:
            monster.draw()
        self.player.draw()
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
            self.grid.recenter()
            return True
        return False

    def spawn(self):
        if random.random() < 0.1:
            grid_coordinate = random.choice(self.grid.spawnable())
            world_coordinate = self.grid.to_world(grid_coordinate)
            self.monsters.append(monsters.Monster(world_coordinate, self))

    def __str__(self):
        return 'Scene {}'.format(self.id)

class Game:
    level = None
    levels = []
    screen = None
    moves = 0
    bg = Color('gray')

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

            Game.screen.fill(Game.bg)
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
        pygame.init()
        Game.screen = ScreenMock()

if __name__ == "__main__":
    g = Game()
    Level()
    g.run()
