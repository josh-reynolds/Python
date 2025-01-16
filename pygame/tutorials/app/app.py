# Tutorial project from https://pygame.readthedocs.io/en/latest/index.html

import pygame
from pygame.locals import *

class Text:
    """Create a text object."""

    def __init__(self, text, pos, **options):
        self.text = text
        self.pos = pos

        App.scene.nodes.append(self)

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

class Scene:
    """Create a new scene (room, level, view)."""
    id = 0
    bg = Color('gray')

    def __init__(self, *args, **kwargs):
        """Append the new scene and make it the current scene."""
        App.scenes.append(self)
        App.scene = self

        # set the instance id and increment the class id
        self.id = Scene.id
        Scene.id += 1
        self.nodes = []
        self.bg = Scene.bg

        if kwargs:
            for key,value in kwargs.items():
                self.__dict__[key] = value

    def draw(self):
        """Draw all objects in the scene."""
        App.screen.fill(self.bg)
        for node in self.nodes:
            node.draw()
        pygame.display.flip()

    def __str__(self):
        return 'Scene {}'.format(self.id)
        
class App:
    """Create a single-window app with multiple scenes."""

    def __init__(self):
        """Initialize pygame and the application."""
        pygame.init()
        self.flags = RESIZABLE
        self.rect = Rect(0, 0, 640, 240)
        App.screen = pygame.display.set_mode(self.rect.size, self.flags)
        App.running = True
        self.shortcuts = {
                (K_x, KMOD_LMETA): 'print("cmd+x")',
                (K_x, KMOD_LALT): 'print("alt+x")',
                (K_x, KMOD_LCTRL): 'print("ctrl+x")',
                (K_x, KMOD_LMETA + KMOD_LSHIFT): 'print("cmd+shift+x")',
                (K_x, KMOD_LMETA + KMOD_LALT): 'print("cmd+alt+x")',
                (K_x, KMOD_LMETA + KMOD_LALT + KMOD_LSHIFT): 'print("cmd+alt+shift+x")',
                (K_q, 0): 'App.running = False',
                (K_f, KMOD_LALT): 'self.toggle_fullscreen()',
                (K_r, KMOD_LALT): 'self.toggle_resizeable()',
                (K_g, KMOD_LALT): 'self.toggle_frame()',
                (K_n, 0): 'self.next_scene()',
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
            App.scene.draw()
            pygame.display.update()

        pygame.quit()

    def do_shortcut(self, event):
        """Find the key/mod combination in the dictionary and execute the cmd."""
        k = event.key
        m = event.mod
        if (k, m) in self.shortcuts:
            exec(self.shortcuts[k, m])

    def toggle_fullscreen(self):
        """Toggle between full screen and windowed screen."""
        self.flags ^= FULLSCREEN
        pygame.display.set_mode((0, 0), self.flags)

    def toggle_resizeable(self):
        """Toggle between resizable and fixed size window."""
        self.flags ^= RESIZABLE
        pygame.display.set_mode(self.rect.size, self.flags)

    def toggle_frame(self):
        """Toggle between frame and no frame window."""
        self.flags ^= NOFRAME
        pygame.display.set_mode(self.rect.size, self.flags)

    def next_scene(self):
        """Change to the next scene in the scenes list."""
        current_scene = App.scene.id
        next_scene = (current_scene + 1) % len(App.scenes)
        App.scene = App.scenes[next_scene]

if __name__ == "__main__":
    App().run()

