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
    
    def update(self):
        pass

    def draw(self):
        if self.level.grid.can_view(self.pos):
            grid_coord = self.level.grid.from_world(self.pos)
            screen_coord = self.level.grid.to_screen(grid_coord)
            #game.Game.screen.blit(self.images[self.current_image], screen_coord)
            game.Game.screen.blit(self.image, screen_coord)



