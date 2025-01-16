# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *

class Text:
    """Create a text object."""

    def __init__(self, text, pos, **options):
        self.text = text
        self.pos = pos

        self.fontname = None
        self.fontsize = 72
        self.fontcolor = Color('black')
        self.set_font()
        self.render()

    def set_font(self):
        """Set the font from its name and size."""
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    def render(self):
        """Render the text into an image."""
        self.img = self.font.render(self.text, True, self.fontcolor)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos

    def draw(self):
        """Draw the image to the screen."""
        App.screen.blit(self.img, self.rect)
            
        
class App:
    """Create a single-window app with multiple scenes."""

    def __init__(self):
        """Initialize pygame and the application."""
        pygame.init()
        flags = RESIZABLE
        App.screen = pygame.display.set_mode((640,240), flags)
        App.t = Text('Pygame App', pos = (20, 20))
        App.running = True
        self.shortcuts = {
                (K_x, KMOD_LMETA): 'print("cmd+x")',
                (K_x, KMOD_LALT): 'print("alt+x")',
                (K_x, KMOD_LCTRL): 'print("ctrl+x")',
                (K_x, KMOD_LMETA + KMOD_LSHIFT): 'print("cmd+shift+x")',
                (K_x, KMOD_LMETA + KMOD_LALT): 'print("cmd+alt+x")',
                (K_x, KMOD_LMETA + KMOD_LALT + KMOD_LSHIFT): 'print("cmd+alt+shift+x")',
                }   

    def run(self):
        """Run the main event loop."""
        while App.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    App.running = False
                if event.type == KEYDOWN:
                    self.do_shortcut(event)

            App.screen.fill(Color('gray'))
            App.t.draw()
            pygame.display.update()

        pygame.quit()

    def do_shortcut(self, event):
        """Find the key/mod combination in the dictionary and execute the cmd."""
        k = event.key
        m = event.mod
        if (k, m) in self.shortcuts:
            exec(self.shortcuts[k, m])

if __name__ == "__main__":
    App().run()

