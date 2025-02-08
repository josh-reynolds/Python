import random
import pygame
from pygame.locals import *
import monsters
import player
import actions
import components
import actor

class Level:
    options = {
            'id': 0,
            'bg': Color('black'),
            'caption': '',
            }

    def __init__(self, **options):
        Game.levels.append(self)
        Game.level = self
        self.id = Level.options['id']
        Level.options['id'] += 1
        self.bg = Level.options['bg']
        self.caption = Level.options['caption']
        self.components = []

        if options:
            self.__dict__.update(options)

        self.rect = Game.screen.get_rect()
        self.img = pygame.Surface(self.rect.size)
        self.img.fill(self.bg)
        self.enter()

    def enter(self):
        pygame.display.set_caption(self.caption)

    def update(self):
        pass
    def draw(self):
        pass
    def define_actions(self):
        pass
    def do_event(self, event):
        pass

class TitleScreen(Level):
    def __init__(self, **options):
        super().__init__(**options)
        self.define_actions()
        self.shortcuts = {}
        self.img = pygame.image.load('./images/title.png')
        self.rect = self.img.get_rect()

    def draw(self):
        Game.screen.blit(self.img, self.rect)
        for component in self.components:
            component.draw()
        pygame.display.flip()

    def do_event(self, event):
        self.components[1].do_event(event)

class EndScreen(Level):
    def __init__(self, **options):
        super().__init__(**options)
        self.define_actions()
        self.shortcuts = {
                K_SPACE: (self.space, 1),
                }

    def update(self):
        for component in self.components:
            component.update()
        # super-kludgy reference to score line here...
        self.components[1].text = 'Your score is {}.'.format(Game.score)
        self.components[1].render()

    def draw(self):
        Game.screen.blit(self.img, self.rect)
        for component in self.components:
            component.draw()
        pygame.display.flip()

    def do_event(self, event):
        if event.type == KEYDOWN:
            self.do_shortcut(event)

    def do_shortcut(self, event):
        k = event.key
        if k in self.shortcuts:
            action = self.shortcuts[k][0]
            action.execute()

    def define_actions(self):
        self.space = actions.Restart(Game)

class Overworld(Level):
    def __init__(self, **options):
        super().__init__(**options)
        self.last_move = ''
        self.action_queue = []
        self.monsters = []
        self.player = player.Player((15,15), self)
        self.effects = []
        self.observers = []

        self.define_actions()
        self.shortcuts = {
                K_a: (self.a, 2),
                K_LEFT: (self.left, 1),
                K_RIGHT: (self.right, 1),
                K_UP: (self.up, 1),
                K_DOWN: (self.down, 1),
                K_SPACE: (self.space, 1),
                K_d: (self.d, 1),
                K_g: (self.g, 1),
                }

    def update(self):
        for component in self.components:
            component.update()
        for monster in self.monsters:
            monster.update()
        self.player.update()
        for effect in self.effects:
            effect.update()

    def draw(self):
        Game.screen.blit(self.img, self.rect)
        for component in self.components:
            component.draw()
        for monster in self.monsters:
            monster.draw()
        self.player.draw()
        for effect in self.effects:
            effect.draw()
        pygame.display.flip()

    def do_event(self, event):
        if event.type == KEYDOWN:
            self.do_shortcut(event)
            Game.message_queue.append((self.last_move, True))
            self.spawn()

    def do_shortcut(self, event):
        k = event.key
        if k in self.shortcuts:
            action = self.shortcuts[k][0]
            key_count = self.shortcuts[k][1]
            if key_count == 1 and not self.action_queue:
                self.last_move = action.name
                self.do_action(action)
            elif key_count == 2 and not self.action_queue:
                self.action_queue.append(k)
                Game.message_queue.append(('Direction?', False))
            elif key_count == 1 and self.action_queue:
                if k == K_UP:
                    direction = (0,-1)
                if k == K_DOWN:
                    direction = (0,1)
                if k == K_LEFT:
                    direction = (-1,0)
                if k == K_RIGHT:
                    direction = (1,0)
                base = self.action_queue.pop()
                action = self.shortcuts[base][0]
                self.last_move = action.name
                self.do_action(action, direction)

    def do_action(self, action, direction=None):
        if direction:
            action.execute(direction)
        else:
            action.execute()
        for observer in self.observers:
            observer.on_notify(self.last_move, self.player.pos)

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def spawn(self):
        if random.random() < 0.1:
            grid_coordinate = random.choice(self.grid.spawnable())
            world_coordinate = self.grid.to_world(grid_coordinate)

            monster_type = 0
            if random.random() < 0.25:
                monster_type = 1
            self.monsters.append(monsters.Monster(world_coordinate, self, monster_type))

    def restart(self):
        self.last_move = ''
        self.action_queue = []
        self.effects = []
        for monster in reversed(self.monsters):
            self.monsters.remove(monster)
            self.remove_observer(monster)
        self.player.restart()
        for component in self.components:
            component.restart()
        for observer in self.observers:
            observer.on_notify(self.last_move, self.player.pos)

    def __str__(self):
        return 'Scene {}'.format(self.id)

    def define_actions(self):
        self.a = actions.Attack(self.player)
        self.left = actions.West(self.player)
        self.right = actions.East(self.player)
        self.up = actions.North(self.player)
        self.down = actions.South(self.player)
        self.space = actions.Pass(self.player)
        self.d = actions.Debug(self)
        self.g = actions.GodMode(self)

    def set_player_name(self):
        self.player.name = Game.player_name

class Game:
    level = None
    levels = []
    current_level = 0
    screen = None
    bg = Color('gray')
    message_queue = []
    score = 0
    player_name = ''

    def __init__(self):
        pygame.init()
        self.flags = 0
        self.rect = Rect(0, 0, 640, 480)
        Game.screen = pygame.display.set_mode(self.rect.size, self.flags)
        Game.running = True
        self.define_actions()
        self.shortcuts = {
                K_q: self.q,
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

    def start(self):
        Game.level = Game.levels[0]
        Game.level.enter()

    def do_shortcut(self, event):
        k = event.key
        if k in self.shortcuts:
            self.shortcuts[k].execute()
            self.last_move = self.shortcuts[k].name

    def define_actions(self):
        self.q = actions.Quit(Game)

    @classmethod
    def next_level(cls):
        cls.current_level += 1
        if cls.current_level == len(cls.levels):
            cls.current_level = len(cls.levels) - 1
        cls.level = cls.levels[cls.current_level]
        if isinstance(cls.level, Overworld):
            cls.level.set_player_name()
        cls.level.enter()

    @classmethod
    def restart(cls):
        cls.score = 0
        cls.current_level = 1
        cls.level = cls.levels[cls.current_level]
        cls.level.restart()
        cls.level.enter()

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
