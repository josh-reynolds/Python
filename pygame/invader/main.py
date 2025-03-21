import math
from enum import Enum
from random import randint
import pygame
from pygame.math import Vector2
from engine import *

WIDTH = 960
HEIGHT = 540
TITLE = "Invader"

LEVEL_WIDTH = 500               ###
TERRAIN_OFFSET_Y = 5               ###
WAVE_COMPLETE_SCREEN_DURATION = 20    ###
HUMAN_START_POS = [(1,2),(1,2)]             ###

class Mock:                    ###
    def draw(self):               ###
        pass                     ###

class KeyboardControls:
    NUM_BUTTONS = 1

    def __init__(self):
        self.previously_down = [False for i in range(KeyboardControls.NUM_BUTTONS)]
        self.is_pressed = [False for i in range(KeyboardControls.NUM_BUTTONS)]

    def update(self):
        for button in range(KeyboardControls.NUM_BUTTONS):
            button_down = self.button_down(button)
            self.is_pressed[button] = button_down and not self.previously_down[button]
            self.previously_down[button] = button_down

    def button_down(self, button):
        if button == 0:
            return keyboard.space

    def button_pressed(self, button):
        return self.is_pressed[button]

class EnemyType(Enum):
    LANDER = 1,            ###

class EnemyState(Enum):
    ALIVE = 1,            ###
    DEAD = 2,              ###

class Enemy:                  ###
    def __init__(self, a, b):   ###
        self.state = 1         ###
    def update(self):      
        pass             ###
    def draw(self, a, b):               ###
        pass                     ###

class Human:            ###
    def __init__(self, a,):   ###
        self.blip = Mock()            ###
        self.dead = False          ###
    def update(self):      
        pass             ###
    def draw(self, a, b):               ###
        pass                     ###

class Player:
    def __init__(self, a):        ###
        self.lives = 3                 ###
        self.shields = 3                 ###
        self.extra_life_tokens = 3                 ###
        self.facing_x = 1          ###
        self.velocity = Vector2(0,0)    ###
        self.x = 1                   ###
        self.y = 1                   ###
        self.tilt_y = 1                   ###
        self.blip = Mock()            ###
    def draw(self, a, b):               ###
        pass                     ###
    def update(self):      
        pass             ###
    def is_carrying_human(self):
        pass             ###
    def level_ended(self, a, b):    ###
        pass            ###

class Radar:
    def __init__(self):
        self.x = 1                   ###
        self.y = 1                   ###
        self.width = 10              ###
        self.height = 10              ###
    def draw(self):
        pass                     ###

class Game:
    def __init__(self, player):
        self.player = player
        self.radar = Radar()
        self.enemies, self.humans, self.lasers, self.bullets = [], [], [], []
        self.score = 0
        self.wave = 0
        self.wave_timer = 0
        self.timer = 0
        self.player_camera_offset_x = WIDTH / 3
        self.terrain_surface = images.terrain
        self.terrain_mask = pygame.mask.from_surface(self.terrain_surface)
        self.new_wave()
        play_music("ambience")

    def new_wave(self):
        self.wave += 1
        num_landers = 4 + self.wave
        num_pods = -1 + self.wave // 2
        num_baiters = 0
        num_mutants = 0
        num_swarmers = 0
        if self.wave % 5 == 0:
            num_landers = 0
            num_pods = 0
            num_baiters = self.wave
            if self.wave % 10 == 0:
                num_swarmers = self.wave // 2
            else:
                num_mutants = self.wave // 2

        self.enemies += [Enemy(-i * 20, EnemyType.LANDER) for i in range(num_landers)]
        self.enemies += [Enemy(-i * 50, EnemyType.POD) for i in range(num_pods)]
        self.enemies += [Enemy(-i * 100, EnemyType.BAITER) for i in range(num_baiters)]
        self.enemies += [Enemy(-i * 10, EnemyType.MUTANT) for i in range(num_mutants)]
        self.enemies += [Enemy(-i * 10, EnemyType.SWARMER) for i in range(num_swarmers)]

        self.humans = []
        for pos in HUMAN_START_POS:
            pos = (pos[0], pos[1] + TERRAIN_OFFSET_Y)
            self.humans.append(Human(pos))

        self.play_sound("new_wave")

    def update(self):
        self.wave_timer += 1
        if self.wave_timer == 0:
            self.new_wave()

        self.timer += 1

        if self.wave_timer > 0 and self.wave_timer % (30 * 60) == 0 and self.player.lives > 0:
            self.enemies.append(Enemy(type=EnemyType.BAITER))

        self.player.update()

        self.lasers = [l for l in self.lasers if not l.update()]
        self.bullets = [b for b in self.bullets if not b.update()]

        for obj in self.enemies + self.humans:
            obj.update()

        self.humans = [h for h in self.humans if not h.dead]

        prev_num_enemies = len(self.enemies)
        self.enemies = [e for e in self.enemies if e.state != EnemyState.DEAD]

        difference = prev_num_enemies - len(self.enemies)
        if difference > 0:
            self.score += 150 * difference

        if self.wave_timer > 0 and len(self.enemies) == 0 \
                and len([human for human in self.humans if human.falling]) == 0 \
                and not self.player.is_carrying_human():
                    self.wave_timer = -WAVE_COMPLETE_SCREEN_DURATION
                    self.player.level_ended(self.get_shield_restore_amount(),
                                            self.get_humans_saved())
                    self.play_sound("wave_complete")

    def draw(self):
        if self.player.facing_x > 0:
            target_camera_offset_x = WIDTH / 3
        else:
            target_camera_offset_x = 2 * WIDTH / 3

        target_camera_offset_x -= self.player.velocity.x * 15
        camera_offset_delta = min(8, max(-8, (target_camera_offset_x - self.player_camera_offset_x)/20))

        self.player_camera_offset_x = math.floor(self.player_camera_offset_x + camera_offset_delta)

        left = -(int(self.player.x - self.player_camera_offset_x) % LEVEL_WIDTH)
        top = max(-int(self.player.y / 4), -100)

        bg_width = images.background.get_width()
        for i in range(5):
            screen.blit("background", (left // 2 + bg_width * i, top // 2))

        screen.blit(self.terrain_surface, (left, top + TERRAIN_OFFSET_Y))
        screen.blit(self.terrain_surface, (left + LEVEL_WIDTH, top + TERRAIN_OFFSET_Y))

        offset_x = -(self.player.x - self.player_camera_offset_x)

        for obj in self.bullets + self.humans + self.enemies + \
                (self.lasers + [self.player] if self.player.tilt_y == 1 
                 else [self.player] + self.lasers):
                    obj.draw(offset_x, top)

        self.draw_ui()

    def draw_ui(self):
        self.radar.draw()

        screen.surface.set_clip((self.radar.x - self.radar.width / 2, self.radar.y,
                                 self.radar.width, self.radar.height))

        for enemy in self.enemies:
            if enemy.state == EnemyState.ALIVE:
                enemy.blip.draw()

        for human in self.humans:
            human.blip.draw()

        self.player.blip.draw()

        screen.surface.set_clip(None)

        for i in range(self.player.lives):
            screen.blit("life", (20 + 20 * i, 21))

        for i in range(self.player.shields):
            screen.blit("armor", (20 + 20 * i, 52))

        for i in range(self.player.extra_life_tokens):
            frame = ((self.timer // 6) + i) % 8
            screen.blit(f"token{frame}", (20 + 20 * i, 83))

        score_text = str(self.score)
        score_width = text_width(score_text, font="font_status")
        draw_text(score_text, WIDTH-score_width-20, 28, font="font_status")

        if self.wave_timer < 0:
            y = (HEIGHT // 2) - 140
            for line in self.get_wave_end_text():
                draw_text(line, WIDTH // 2, y, True)
                y += 65

    def get_wave_end_text(self):
        saved = self.get_humans_saved()
        i = (self.wave_timer + WAVE_COMPLETE_SCREEN_DURATION) // (WAVE_COMPLETE_SCREEN_DURATION //4)
        lines = [f"WAVE {self.wave} COMPLETE"]
        if i >= 1:
            lines.append(f"{saved} HUMAN{'' if saved == 1 else 'S'} SAVED")
        if i >= 2:
            shields = self.get_shield_restore_amount()
            lines.append(f"{shields} SHIELD{'' if shields == 1 else 'S'} RESTORED")
        if i >= 3 and saved == 10:
            if self.player.extra_life_tokens == 0:
                lines.append("EXTRA LIFE")
            else:
                lines.append("LIFE TOKEN GAINED")
        return lines

    def get_shield_restore_amount(self):
        return min(self.get_humans_saved() // 2, 5)

    def get_humans_saved(self):
        return len([human for human in self.humans if not human.exploding])

    def play_sound(self, name, count=1, volume=1):
        if volume <= 0 or (self.player.lives == 0 and self.player.timers[Player.Timer.HURT] < -1000):
            return
        try:
            fullname = name + str(randint(0, count-1))
            if volume < 1:
                sound = pygame.mixer.Sound("sounds/" + fullname + ".ogg")
                sound.set_volume(volume)
            else:
                sound = getattr(sounds, fullname)
            sound.play()
        except Exception as e:
            print(e)

def get_char_image_and_width(char, font):
    if char == " ":
        return None, 22
    else:
        image = getattr(images, font + "0" + str(ord(char)))
        return image, image.get_width()

def text_width(text, font="font"):
    return sum([get_char_image_and_width(c, font)[1] for c in text])

def draw_text(text, x, y, center=False, font="font"):
    if center:
        x -= text_width(text) // 2

    for char in text:
        image, width = get_char_image_and_width(char, font)
        if image is not None:
            screen.blit(image, (x, y))
        x += width

class State(Enum):
    TITLE = 1
    PLAY = 2
    GAME_OVER = 3

def update():
    global state, game, state_timer

    keyboard_controls.update()

    state_timer += 1

    if state == State.TITLE:
        for controls in (keyboard_controls,):     # comments indicate GitHub has controller support too
            if controls is not None and controls.button_pressed(0):
                state = State.PLAY
                state_timer = 0
                game = Game(Player(controls))
                break

    elif state == State.PLAY:
        if game.player.lives <= 0:
            state = State.GAME_OVER
            state_timer = 0
        else:
            game.update()

    elif state == State.GAME_OVER:
        game.update()
        if state_timer > 60:
            for controls in (keyboard_controls,):     # comments indicate GitHub has controller support too
                if controls is not None and controls.button_pressed(0):
                    state = State.TITLE
                    state_timer = 0
                    game = None
                    play_music("menu_theme")

def draw():
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit(f"start{(state_timer // 4) % 14}", (WIDTH // 2 - 350 // 2, 450))

    elif state == State.PLAY:
        game.draw()

    elif state == State.GAME_OVER:
        game.dxraw()
        draw_text("GAME OVER", WIDTH // 2, (HEIGHT // 2) - 100, True)

def play_music(name):
    try:
        music.play(name)
    #except Exception:
        #pass
    except Exception as e:         ###
        print(e)                   ###

keyboard_controls = KeyboardControls()

state = State.TITLE
state_timer = 0

run()
