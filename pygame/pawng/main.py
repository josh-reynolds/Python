# based on Boing! in Code the Classics Vol. 1
# those projects are based on Pygame Zero - I am converting
# to 'raw' Pygame instead

import math
import random
import pygame
from pygame.locals import *
from enum import Enum

SIZE = (800, 480)
WIDTH, HEIGHT = SIZE
TITLE = "Pawng!"

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
PLAYER_SPEED = 6
MAX_AI_SPEED = 6

def normalized(x, y):
    length = math.hypot(x, y)
    return (x/length, y/length)

def sign(x):
    return -1 if x < 0 else 1


#--------------------------------------------------------
class Actor:                        # replacing Pygame Zero code
    def __init__(self, image, pos):
        self.image = image
        self.x = pos[0]
        self.y = pos[1]

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Music:
    def __init__(self):
        pass

    def play(self, song):
        filename = './music/' + song + '.ogg'
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)     # repeat indefinitely

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

music = Music()
#--------------------------------------------------------

class Impact(Actor):
    def __init__(self, pos):
        super().__init__("blank", pos)
        self.time = 0

    def update(self):
        self.image = "impact" + str(self.time // 2)
        self.time += 1

    def __repr__(self):
        return "Impact(" + str(self.x) + "," + str(self.y) + ")"

class Ball(Actor):
    def __init__(self, dx):
        super().__init__("ball", (0,0))
        self.x, self.y = HALF_WIDTH, HALF_HEIGHT
        self.dx, self.dy = dx, 0
        self.speed = 5

    def update(self):
        for i in range(self.speed):
            original_x = self.x
            self.x += self.dx
            self.y += self.dy
            self.pos = (self.x, self.y)       # added this line, not from original sources

            if abs(self.x - HALF_WIDTH) >= 344 and abs(original_x - HALF_WIDTH) < 344:
                if self.x < HALF_WIDTH:
                    new_dir_x = 1
                    bat = game.bats[0]
                else:
                    new_dir_x = -1
                    bat = game.bats[1]

                difference_y = self.y - bat.y

                if difference_y > -64 and difference_y < 64:
                    self.dx = -self.dx
                    self.dy += difference_y / 128
                    self.dy = min(max(self.dy, -1), 1)
                    self.dx, self.dy = normalized(self.dx, self.dy)
                    game.impacts.append(Impact((self.x - new_dir_x * 10, self.y)))
                    self.speed += 1
                    game.ai_offset = random.randint(-10, 10)
                    bat.timer = 10

                    game.play_sound("hit", 5)
                    if self.speed <= 10:
                        game.play_sound("hit_slow", 1)
                    elif self.speed <= 12:
                        game.play_sound("hit_medium", 1)
                    elif self.speed <= 16:
                        game.play_sound("hit_fast", 1)
                    else:
                        game.play_sound("hit_veryfast", 1)

                if abs(self.y - HALF_HEIGHT) > 220:
                    self.dy = -self.dy
                    self.y += self.dy
                    game.impacts.append(Impact(self.pos))
                    game.play_sound("bounce", 5)
                    game.play_sound("bounce_synth", 1)

    def out(self):
        return self.x < 0 or self.x > WIDTH

    def __repr__(self):
        return "Ball(" + str(self.dx) + ")"

class Bat(Actor):
    def __init__(self, player, move_func=None):
        x = 40 if player == 0 else 760
        y = HALF_HEIGHT
        super().__init__("blank", (x, y))

        self.player = player
        self.score = 0

        if move_func != None:
            self.move_func = move_func
        else:
            self.move_func = self.ai

        self.timer = 0

    def update(self):
        self.timer -= 1
        y_movement = self.move_func()
        self.y = min(400, max(80, self.y + y_movement))

        frame = 0
        if self.timer > 0:
            if game.ball.out():
                frame = 2
            else:
                frame = 1

        self.image = 'bat' + str(self.player) + str(frame)

    def ai(self):
        x_distance = abs(game.ball.x - self.x)
        target_y_1 = HALF_HEIGHT
        target_y_2 = game.ball.y + game.ai_offset
        weight1 = min(1, x_distance / HALF_WIDTH)
        weight2 = 1 - weight1
        target_y = (weight1 * target_y_1) + (weight2 * target_y_2)
        return min(MAX_AI_SPEED, max(-MAX_AI_SPEED, target_y - self.y))

    def __repr__(self):
        return "Bat(" + str(self.player) + ", move_func)"

class Game:
    def __init__(self, controls=(None, None)):
        self.bats = [Bat(0, controls[0]), Bat(1, controls[1])]
        self.ball = Ball(-1)
        self.impacts = []
        self.ai_offset = 0

    def update(self):
        for obj in self.bats + [self.ball] + self.impacts:
            obj.update()

        for i in range(len(self.impacts) - 1, -1, -1):
            if self.impacts[i].time >= 10:
                del self.impacts[i]

        if self.ball.out():
            scoring_player = 1 if self.ball.x < WIDTH // 2 else 0
            losing_player = 1 - scoring_player

            if self.bats[losing_player].timer < 0:
                self.bats[scoring_player].score += 1
                game.play_sound("score_goal", 1)
                self.bats[losing_player].timer = 20

            elif self.bats[losing_player].timer == 0:
                direction = -1 if losing_player == 0 else 1
                self.ball = Ball(direction)

    def draw(self):
        screen.blit("table", (0,0))

        for p in (0,1):
            if self.bats[p].timer > 0 and game.ball.out():
                screen.blit("effect" + str(p), (0,0))

        for obj in self.bats + [self.ball] + self.impacts:
            obj.draw()
        
        for p in(0,1):
            score = f"{self.bats[p].score:02d}"

            for i in (0,1):
                color = "0"
                other_p = 1 - p
                if self.bats[other_p].timer > 0 and game.ball.out():
                    color = "2" if p == 0 else "1"
                image = "digit" + color + str(score[i])
                screen.blit(image, (255 + (160 * p) + (i * 55), 46))

    def play_sound(self, name, count=1):
        if self.bats[0].move_func != self.bats[0].ai:
            try:
                getattr(sounds, name + str(random.randint(0, count - 1))).play()
            except:
                pass

def p1_controls():
    move = 0
    if keyboard.z or keyboard.down:
        move = PLAYER_SPEED
    elif keyboard.a or keyboard.up:
        move = -PLAYER_SPEED
    return move

def p2_controls():
    move = 0
    if keyboard.m:
        move = PLAYER_SPEED
    elif keyboard.k:
        move = -PLAYER_SPEED
    return move

class State(Enum):
    MENU = 1
    PLAY = 2
    GAME_OVER = 3

num_players = 1
space_down = False

def update():
    global state, game, num_players, space_down
    space_pressed = False
    if keyboard.space and not space_down:
        space_pressed = True
    space_down = keyboard.space

    if state == State.MENU:
        if space_pressed:
            state = State.PLAY
            controls = [p1_controls]
            controls.append(p2_controls if num_players == 2 else None)
            game = Game(controls)
        else:
            if num_players == 2 and keyboard.up:
                sounds.up.play()
                num_players = 1
            elif num_players == 1 and keyboard.down:
                sounds.down.play()
                num_players = 2

            game.update()

    elif state == State.PLAY:
        if max(game.bats[0].score, game.bats[1].score) >= 9:
            state = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if space_pressed:
            state = State.MENU
            num_players = 1
            game = Game()

def draw():
    game.draw()

    if state == State.MENU:
        menu_image = "menu" + str(num_players - 1)
        screen.blit(menu_image, (0, 0))

    elif state == State.GAME_OVER:
        screen.blit("over", (0, 0))

try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)

    music.play('theme')
    music.set_volume(0.3)
except:
    pass

state = State.MENU
game = Game()

#--------------------------------------------------------
class Keyboard:
    def __init__(self):
        self.reset()

    def reset(self):
        self.space = False
        self.up = False
        self.down = False
        self.a = False
        self.k = False
        self.m = False
        self.z = False

    def __repr__(self):
        return("Keyboard: {}, {}, {}, {}, {}, {}, {}".format(self.space, self.up,
                                                             self.down, self.a,
                                                             self.k, self.m, self.z))

class Screen:
    def __init__(self, size):
        self.display = pygame.display.set_mode(size)
        self.images = {}

    def fill(self, color):
        self.display.fill(color)

    def blit(self, image, position):
        if image not in self.images:
            image_name = './images/' + image + '.png'
            self.images[image] = pygame.image.load(image_name)
        self.display.blit(self.images[image], position)

class Sounds:
    def __init__(self):
        self.bounce0 = pygame.mixer.Sound('./sounds/bounce0.ogg')
        self.bounce1 = pygame.mixer.Sound('./sounds/bounce1.ogg')
        self.bounce2 = pygame.mixer.Sound('./sounds/bounce2.ogg')
        self.bounce3 = pygame.mixer.Sound('./sounds/bounce3.ogg')
        self.bounce4 = pygame.mixer.Sound('./sounds/bounce4.ogg')
        self.bounce_synth0 = pygame.mixer.Sound('./sounds/bounce_synth0.ogg')
        self.down = pygame.mixer.Sound('./sounds/down.ogg')
        self.hit0 = pygame.mixer.Sound('./sounds/hit0.ogg')
        self.hit1 = pygame.mixer.Sound('./sounds/hit1.ogg')
        self.hit2 = pygame.mixer.Sound('./sounds/hit2.ogg')
        self.hit3 = pygame.mixer.Sound('./sounds/hit3.ogg')
        self.hit4 = pygame.mixer.Sound('./sounds/hit4.ogg')
        self.hit_fast0 = pygame.mixer.Sound('./sounds/hit_fast0.ogg')
        self.hit_medium0 = pygame.mixer.Sound('./sounds/hit_medium0.ogg')
        self.hit_slow0 = pygame.mixer.Sound('./sounds/hit_slow0.ogg')
        self.hit_synth0 = pygame.mixer.Sound('./sounds/hit_synth0.ogg')
        self.hit_veryfast0 = pygame.mixer.Sound('./sounds/hit_veryfast0.ogg')
        self.score_goal0 = pygame.mixer.Sound('./sounds/score_goal0.ogg')
        self.up = pygame.mixer.Sound('./sounds/up.ogg')

pygame.init()
screen = Screen(SIZE)
keyboard = Keyboard()
sounds = Sounds()

running = True
while running:
    pygame.time.Clock().tick(60)
    keyboard.reset()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_q:
                running = False
            if event.key == K_SPACE:
                keyboard.space = True
            if event.key == K_UP:
                keyboard.up = True
            if event.key == K_DOWN:
                keyboard.down = True
            if event.key == K_a:
                keyboard.a = True
            if event.key == K_k:
                keyboard.k = True
            if event.key == K_m:
                keyboard.m = True
            if event.key == K_z:
                keyboard.z = True

    screen.fill(Color('white'))
    update()
    draw()
    pygame.display.update()

pygame.quit()
