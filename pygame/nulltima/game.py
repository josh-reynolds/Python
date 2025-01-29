import random
import pygame
from pygame.locals import *
import actor
import monsters
import player
import actions

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

    def update(self):
        pass

    def render(self):
        pass

    def draw(self):
        pass
        
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

    def draw(self):
        Game.screen.blit(self.img, self.rect)

class StatusDisplay(Component):
    def __init__(self, pos):
        super().__init__(pos)
        self.target.add_observer(self)
        self.on_notify(None, None)
        self.render()

    def render(self):
        self.width = 200

        contents = self.generate_contents()
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

class GameStatusDisplay(StatusDisplay):
    def __init__(self, pos):
        self.bg = Color('gray33')
        self.moves = -1
        self.target = Game.level
        super().__init__(pos)

    def generate_contents(self):
        return ["moves: " + str(self.moves), 
                "coordinates: " + str(self.player_position)]

    def on_notify(self, last_move, player_position):
        self.moves += 1
        self.player_position = self.target.player.pos

class PlayerStatusDisplay(StatusDisplay):
    def __init__(self, pos):
        self.bg = Color('gray50')
        self.name = ""
        self.hit_points = ""
        self.target = Game.level.player
        super().__init__(pos)

    def generate_contents(self):
        return ["name: " + str(self.name), 
                "hit points: " + str(self.hit_points)]

    def on_notify(self, name, hit_points):
        self.name = self.target.name
        self.hit_points = self.target.hit_points

class Console(Component):
    def __init__(self, pos):
        super().__init__(pos)
        self.bg = Color('gray50')
        self.lines = []
        self.maxlines = 8
        self.prompt = '|>  '
        self.prompt_pos = 0
        self.prompt_color = self.bg
        self.time = 0
        self.animation_delay = 40
        Game.message_queue.append('Start')
        self.render()

    def update(self):
        for item in reversed(Game.message_queue):
            if self.lines:
                self.lines.pop()                  # remove the empty prompt line
            self.lines.append(self.prompt + item)
            self.lines.append(self.prompt)        # and put it back again...
            Game.message_queue.remove(item)
        if len(self.lines) > self.maxlines:
            self.lines.pop(0)
        self.time += 1
        if self.time > self.animation_delay:
            self.time = 0
            if self.prompt_color == self.bg:
                self.prompt_color = self.fontcolor
            else:
                self.prompt_color = self.bg

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

    def draw(self):
        self.render()
        cursor_rect = (30, self.prompt_pos, self.fontsize/6, self.fontsize)
        pygame.draw.rect(self.img, self.prompt_color, cursor_rect)
        Game.screen.blit(self.img, self.rect)

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
        self.bg = Level.options['bg']
        self.file = Level.options['file']
        self.caption = Level.options['caption']
        self.last_move = ''

        self.components = []
        self.monsters = []
        self.player = player.Player((15,15), self)
        self.observers = []

        self.define_actions()
        self.shortcuts = {
                (K_a, 0): self.a,
                (K_LEFT, 0): self.left,
                (K_RIGHT, 0): self.right,
                (K_UP, 0): self.up,
                (K_DOWN, 0): self.down,
                (K_SPACE, 0): self.space,
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
            Game.message_queue.append(self.last_move)
            for observer in self.observers:
                observer.on_notify(self.last_move, self.player.pos)
            self.spawn()

    def do_shortcut(self, event):
        k = event.key
        m = event.mod
        if (k, m) in self.shortcuts:
            self.shortcuts[k,m].execute()
            self.last_move = self.shortcuts[k,m].name

    def add_observer(self, observer):
        self.observers.append(observer)

    def spawn(self):
        if random.random() < 0.1:
            grid_coordinate = random.choice(self.grid.spawnable())
            world_coordinate = self.grid.to_world(grid_coordinate)
            self.monsters.append(monsters.Monster(world_coordinate, self))

    def __str__(self):
        return 'Scene {}'.format(self.id)

    def define_actions(self):
        self.a = actions.Attack(self.player)
        self.left = actions.West(self.player)
        self.right = actions.East(self.player)
        self.up = actions.North(self.player)
        self.down = actions.South(self.player)
        self.space = actions.Pass(self.player)

class Game:
    level = None
    levels = []
    screen = None
    bg = Color('gray')
    message_queue = []

    def __init__(self):
        pygame.init()
        self.flags = RESIZABLE                   # not handling resize properly yet
        self.rect = Rect(0, 0, 640, 480)
        Game.screen = pygame.display.set_mode(self.rect.size, self.flags)
        Game.running = True
        self.define_actions()
        self.shortcuts = {
                (K_q, 0): self.q,
                }

    def run(self):
        while Game.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    Game.running = False
                if event.type == KEYDOWN:
                    self.do_shortcut(event)

                Game.level.do_event(event)

            Game.screen.fill(Game.bg)
            Game.level.update()
            Game.level.draw()
            pygame.display.update()

        pygame.quit()

    def do_shortcut(self, event):
        k = event.key
        m = event.mod
        if (k, m) in self.shortcuts:
            self.shortcuts[k,m].execute()
            self.last_move = self.shortcuts[k,m].name

    def define_actions(self):
        self.q = actions.Quit(Game)

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
