import pygame

RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
LT_GRN  = (150, 255, 150)
BLUE    = (  0,   0, 255)
CYAN    = (  0, 255, 255)
MAGENTA = (255,   0, 255)
YELLOW  = (255, 255,   0)
WHITE   = (255, 255, 255)
GREY    = (150, 150, 150)
BLACK   = (  0,   0,   0)

SIZE   = (640, 480)

width, height = SIZE

def draw_text(text, pos):
    img = font.render(text, True, BLACK)
    screen.blit(img, pos)

pygame.init()
screen = pygame.display.set_mode(SIZE)
font = pygame.font.Font(None, 24)
