import pygame
import game


class Effect:
    pass

# starting to look a lot like an Actor...
class MeleeAttack(Effect):
    image = None

    def __init__(self, coordinate, level):
        self.pos = coordinate
        self.level = level
        if not MeleeAttack.image:
            MeleeAttack.image = pygame.image.load("./images/attack.png")
        self.image = MeleeAttack.image
        self.time = 0
        self.lifespan = 20
        self.sound = pygame.mixer.Sound('./audio/slap.wav')
        self.played = False
    
    def update(self):
        self.time += 1
        if self.time > self.lifespan:
            self.level.effects.remove(self)

    def draw(self):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.from_world(self.pos)
            screen_coord = self.level.grid.to_screen(grid_coord)
            game.Game.screen.blit(self.image, screen_coord)
            if not self.played:           # we only want the sound effect
                self.sound.play()         # on the first animation frame
                self.played = True



