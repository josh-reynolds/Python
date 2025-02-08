import unittest
import pygame
from pygame.locals import *
import game

class Component:
    def __init__(self, pos):
        self.pos = pos
        self.fontname = None
        self.fontsize = 24
        self.fontcolor = Color('white')
        self.set_font()
        game.Game.level.components.append(self)

    def set_font(self):
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    def update(self):
        pass

    def render(self):
        pass

    def draw(self):
        pass

    def restart(self):
        pass
        
class Text(Component):
    def __init__(self, text, pos):
        super().__init__(pos)
        self.text = text
        self.render()

    def render(self):
        self.img = self.font.render(self.text, True, self.fontcolor)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

    def draw(self):
        game.Game.screen.blit(self.img, self.rect)

class EditableText(Component):
    def __init__(self, text, pos):
        super().__init__(pos)
        self.text = text
        self.render()

    def render(self):
        self.img = self.font.render(self.text, True, self.fontcolor)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

    def draw(self):
        self.render()
        game.Game.screen.blit(self.img, self.rect)

    def do_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == K_RETURN:
                game.Game.player_name = self.text
                game.Game.next_level()
            else:
                self.insert_text(event.unicode)

    def insert_text(self, text):
        self.text += text

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
        game.Game.screen.blit(self.img, self.rect)

class GameStatusDisplay(StatusDisplay):
    def __init__(self, pos):
        self.bg = Color('gray33')
        self.moves = -1
        self.target = game.Game.level
        super().__init__(pos)

    def generate_contents(self):
        return ["moves: " + str(self.moves), 
                "coordinates: " + str(self.player_position)]

    def on_notify(self, last_move, player_position):
        self.moves += 1
        self.player_position = self.target.player.pos

    def restart(self):
        self.moves = -1

class PlayerStatusDisplay(StatusDisplay):
    def __init__(self, pos):
        self.bg = Color('gray50')
        self.name = ""
        self.hit_points = ""
        self.experience = ""
        self.target = game.Game.level.player
        super().__init__(pos)

    def generate_contents(self):
        return ["name: " + str(self.name), 
                "hit points: " + str(self.hit_points),
                "experience: " + str(self.experience)]

    def on_notify(self, name, hit_points):
        self.name = self.target.name
        self.hit_points = self.target.hit_points
        self.experience = self.target.experience
        if self.hit_points < 1:
            game.Game.next_level()

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
        game.Game.message_queue.append(('Start', False))
        self.render()

    def update(self):
        for item in reversed(game.Game.message_queue):
            if self.lines:
                self.lines.pop()                  # remove the empty prompt line

            if item[1]:
                self.lines.append(self.prompt + item[0])
            else:
                self.lines.append(item[0])

            self.lines.append(self.prompt)        # and put it back again...
            game.Game.message_queue.remove(item)
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
        game.Game.screen.blit(self.img, self.rect)

    def restart(self):
        self.lines = []
        self.prompt_pos = 0
        game.Game.message_queue.append(('Start', False))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
