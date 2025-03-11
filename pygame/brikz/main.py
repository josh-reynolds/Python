from engine import *

WIDTH = 800
HEIGHT = 480
TITLE = 'Brikz'

class Game:
    def draw(self):
        pass

class State:
    TITLE = None           ###

def update():
    pass

def draw():
    game.draw()
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit("startgame", (20,80))
        screen.blit(f"start{(total_frames // 4) % 13}", (WIDTH//2 - 250//2, 530))
    elif state == State.GAME_OVER:
        screen.blit(f"gameover{(total_frames // 4) % 15}", (WIDTH//2 - 450//2, 450))

state = State.TITLE
game = Game()         ###
total_frames = 0

run()
