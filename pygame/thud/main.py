import json
import sys
import time
from enum import Enum
from random import choice, randint
from abc import ABC, abstractmethod
import pygame
from pygame import Rect, mixer
from pygame.math import Vector2
from engine import *

# version checks not present in book sources
if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

engine = sys.modules["engine"]
engine_version = [int(s) if s.isnumeric() else s
                  for s in engine.__version__.split('.')]

if engine_version < [1,3]:
    print(f"This game requires at least version 1.3 of the engine. "
          f"You are using version {engine.__version__}. Please upgrade.")
    sys.exit()

WIDTH = 800
HEIGHT = 480
TITLE = "Thud!"

SPECIAL_FONT_SYMBOLS = {'xb_a' : '%'}
SPECIAL_FONT_SYMBOLS_INVERSE = dict((v,k) for k,v in SPECIAL_FONT_SYMBOLS.items())

INTRO_ENABLED = True
HEALTH_STAMINA_BAR_WIDTH = 235
HEALTH_STAMINA_BAR_HEIGHT = 26
FLYING_KICK_VEL_X = 3
FLYING_KICK_VEL_Y = -8
JUMP_GRAVITY = 0.4
THROWN_GRAVITY = 0.025
WEAPON_GRAVITY = 0.5
BARREL_THROW_VEL_X = 4
BARREL_THROW_VEL_Y = 0
PLAYER_THROW_VEL_X = 5
PLAYER_THROW_VEL_Y = 0.5
BASE_STAMINA_DAMAGE_MULTIPLIER = 100
MIN_STAMINA = -100
MIN_WALK_Y = 310
ENEMY_APPROACH_PLAYER_DISTANCE = 85
ENEMY_APPROACH_PLAYER_DISTANCE_SCOOTERBOY = 140
ENEMY_APPROACH_PLAYER_DISTANCE_BARREL = 180
ANCHOR_CENTER = ('center', 'center')
ANCHOR_CENTER_BOTTOM = ('center', 'bottom')
BACKGROUND_TILE_SPACING = 290

DEBUG_LOGGING_ENABLED = False
DEBUG_SHOW_SCROLL_POS = False
DEBUG_SHOW_BOUNDARY = False
DEBUG_SHOW_ATTACKS = False
DEBUG_SHOW_TARGET_POS = False
DEBUG_SHOW_ANCHOR_POINTS = False
DEBUG_SHOW_HIT_AREA_WIDTH = False
DEBUG_SHOW_LOGS = False
DEBUG_SHOW_HEALTH_AND_STAMINA = False
DEBUG_PROFILING = False

debug_drawcalls = []

class Profiler:
    def __init__(self, name=""):
        self.start_time = time.perf_counter()
        self.name = name

    def get_ms(self):
        endTime = time.perf_counter()
        diff = endTime - self.start_time
        return diff * 1000

    def __str__(self):
        return f"{self.name}: {self.get_ms()}ms"

BACKGROUND_TILES = ["wall_end1", "wall_fill1", "wall_fill5", "wall_fill2", "alley1", "wall_end6", "wall_fill7",
                    "wall_fill5", "alley2", "wall_end3", "wall_fill3", "wall_fill4", "wall_fill8", "alley5",
                    "wall_end2", "alley3", "wall_end4", "wall_fill6", "alley6", "wall_end8", "wall_fill4", 
                    "alley7", "wall_end5", "alley8", "set_pc_a1", "set_pc_a2", "alley9", "set_pc_b1", 
                    "set_pc_b2", "set_pc_b3", "wall_end3", "wall_fill3", "alley8", "set_pc_a1", "set_pc_a2", 
                    "wall_fill2", "con_start2", "con_end1a", "con_end2", "con_start2", "con_end1", 
                    "con_fill1", "con_end2a", "con_start2", "con_end1a", "con_fill1a", "con_end2", 
                    "set_pc_c1", "set_pc_c2", "set_pc_c3", "con_start1", "con_end1", "con_fill1", 
                    "con_fill2", "con_fill1a", "con_fill2a", "wall_end1", "alley10", "steps_end1a", 
                    "steps_fill1a", "steps_fill2a", "steps_end2a", "flats_alley1", "steps_end1", 
                    "steps_end2", "flats_alley1",  "flats_end1a", "steps_fill2", "steps_fill1", 
                    "flats_end2a", "flats_alley2", "set_pc_d1", "set_pc_d2", "set_pc_d3", "steps_end2a"]

fullscreen_black_bmp = pygame.Surface((WIDTH,HEIGHT))
fullscreen_black_bmp.fill((0,0,0))

def clamp(value, min_val, max_val):
    return min(max(value, min_val), max_val)

def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min) * (old_val - old_min) / (old_max - old_min) + new_min

def remap_clamp(old_val, old_min, old_max, new_min, new_max):
    lower_limit = min(new_min, new_max)
    upper_limit = max(new_min, new_max)
    return min(upper_limit,
               max(lower_limit, remap(old_val, old_min, old_max, new_min, new_max)))

def sign(x):
    if x == 0:
        return 0
    else:
        return -1 if x < 0 else 1

def move_towards(n, target, speed):
    if n < target:
        return min(n + speed, target), 1
    elif n > target:
        return max(n - speed, target), -1
    else:
        return n,0

class Controls(ABC):
    NUM_BUTTONS = 4

    def __init__(self):
        self.button_previously_down = [False for i in range(Controls.NUM_BUTTONS)]
        self.is_button_pressed = [False for i in range(Controls.NUM_BUTTONS)]

    def update(self):
        # Call each frame to update button status
        for button in range(Controls.NUM_BUTTONS):
            button_down = self.button_down(button)
            self.is_button_pressed[button] = button_down and not self.button_previously_down[button]
            self.button_previously_down[button] = button_down

    @abstractmethod
    def get_x(self):
        # Overridden by subclasses
        pass

    @abstractmethod
    def get_y(self):
        # Overridden by subclasses
        pass

    @abstractmethod
    def button_down(self, button):
        # Overridden by subclasses
        pass

    def button_pressed(self, button):
        return self.is_button_pressed[button]

class KeyboardControls(Controls):
    def get_x(self):
        if keyboard.left:
            return -1
        elif keyboard.right:
            return 1
        else:
            return 0

    def get_y(self):
        if keyboard.up:
            return -1
        elif keyboard.down:
            return 1
        else:
            return 0

    def button_down(self, button):
        if button == 0:
            return keyboard.space or keyboard.z or keyboard.lctrl   # punch
        elif button == 1:
            return keyboard.x or keyboard.lalt   # kick
        elif button == 2:
            return keyboard.c or keyboard.lshift  # elbow
        elif button == 3:
            return keyboard.a   # flying kick

class JoystickControls(Controls):
    def __init__(self, joystick):
        super().__init__()
        self.joystick = joystick
        joystick.init()

    def get_axis(self, axis_num):
        if self.joystick.get_numhats() > 0 and self.joystick.get_hat(0)[axis_num] != 0:
            return self.joystick.get_hat(0)[axis_num] * (-1 if axis_num == 1 else 1)

        axis_value = self.joystick.get_axis(axis_num)
        if abs(axis_value) < 0.6:
            return 0
        else:
            return 1 if axis_value > 0 else -1

    def get_x(self):
        return self.get_axis(0)

    def get_y(self):
        return self.get_axis(1)

    def button_down(self, button):
        if self.joystick.get_numbuttons() <= button:
            print("Warning: main controller does not have enough buttons!")
            return False
        return self.joystick.get_button(button) != 0

class Attack:
    def __init__(self, sprite=None, strength=None, anim_time=None, frame_time=5,
                 frames=0, hit_frames=(), recovery_time=0, reach=80, throw=False,
                 grab=False, combo_next=None, flyingkick=False, stamina_cost=10,
                 rear_attack=False, stamina_damage_multiplier=1,
                 stun_time_multiplier=1, initial_sound=None, hit_sound=None):
        if combo_next is not None:
            combo_next = {int(key):value for (key,value) in combo_next.items()}
        self.sprite = sprite
        self.strength = strength
        self.recovery_time = recovery_time
        self.anim_time = anim_time
        self.frame_time = frame_time
        self.frames = frames
        self.hit_frames = hit_frames
        self.reach = reach
        self.throw = throw
        self.grab = grab
        self.combo_next = combo_next
        self.flying_kick = flyingkick
        self.stamina_cost = stamina_cost
        self.rear_attack = rear_attack
        self.stamina_damage_multiplier = stamina_damage_multiplier
        self.stun_time_multiplier = stun_time_multiplier
        self.initial_sound = initial_sound
        self.hit_sound = hit_sound

with open("attacks.json") as attacks_file:
    ATTACKS = json.load(attacks_file)
    for key, value in ATTACKS.items():
        ATTACKS[key] = Attack(**value)

class ScrollHeightActor(Actor):
    def __init__(self, img, pos, anchor=None, separate_shadow=False):
        super().__init__(img, pos, anchor=anchor)
        self.vpos = Vector2(pos)
        self.height_above_ground = 0
        if separate_shadow:
            self.shadow_actor = Actor("blank", pos, anchor=anchor)
        else:
            self.shadow_actor = None

    def draw(self, offset):
        if self.shadow_actor is not None:
            self.shadow_actor.pos = (self.vpos.x - offset.x, self.vpos.y - offset.y)
            self.shadow_actor.image = "blank" if self.image == "blank" else self.image + "_shadow"
            self.shadow_actor.draw()

        self.pos = (self.vpos.x - offset.x,
                    self.vpos.y - offset.y - self.height_above_ground)
        super().draw()
        if DEBUG_SHOW_ANCHOR_POINTS:
            screen.draw.circle(self.pos, 5, (255,255,255))

    def on_screen(self):
        return 0 < self.x < WIDTH

    def get_draw_order_offset(self):
        return 0

class Fighter(ScrollHeightActor, ABC):
    WEAPON_HOLD_HEIGHT = 100

    class FallingState(Enum):
        STANDING = 0
        FALLING = 1
        GETTING_UP = 2
        GRABBED = 3
        THROWN = 4

    def log(self, str):
        if DEBUG_LOGGING_ENABLED:
            l = f"{game.timer} {str} {self.vpos}"
            print(self, l)
            self.logs.append(l)

    def __init__(self, pos, anchor, speed, sprite, health, anim_update_rate=8,
                 stamina=500, half_hit_area=Vector2(25,20), lives=1,
                 color_variant=None, separate_shadow=False, hit_sound=None):
        super().__init__("blank", pos, anchor, separate_shadow=separate_shadow)

        self.speed = speed
        self.sprite = sprite
        self.anim_update_rate = anim_update_rate
        self.facing_x = 1
        self.frame = 0
        self.last_attack = None
        self.attack_timer = 0
        self.falling_state = Fighter.FallingState.STANDING
        self.walking = False
        self.vel = Vector2(0,0)
        self.pickup_animation = None
        self.hit_timer = 0
        self.hit_frame = 0
        self.stamina = stamina
        self.max_stamina = stamina
        self.half_hit_area = half_hit_area
        self.health = health
        self.start_health = health
        self.lives = lives
        self.color_variant = color_variant
        self.hit_sound = hit_sound
        self.weapon = None
        self.just_knocked_off_scooter = False
        self.use_die_animation = False
        self.logs = []

    def update(self):
        self.attack_timer -= 1

        if self.height_above_ground > 0 or self.vel.y != 0:
            self.vpos.x += self.vel.x
            self.vel.y += THROWN_GRAVITY if self.falling_state == Fighter.FallingState.THROWN \
                    else JUMP_GRAVITY
            self.height_above_ground -= self.vel.y
            self.apply_movement_boundaries(self.vel.x, 0)
            if self.height_above_ground < 0:
                self.height_above_ground = 0
                self.vel.x = 0
                self.vel.y = 0
                self.hit_timer = 0

        if self.falling_state == Fighter.FallingState.FALLING:
            self.vpos.x += self.vel.x
            self.vel.x, _ = move_towards(self.vel.x, 0, 0.5)
            self.apply_movement_boundaries(self.vel.x, 0)
            self.frame += 1
            if self.frame > 120:
                if self.health > 0:
                    self.falling_state = Fighter.FallingState.GETTING_UP
                    self.frame = 0
                    self.stamina = self.max_stamina
                else:
                    if self.frame > 240:
                        self.lives -= 1
                        if self.lives > 0:
                            self.health = self.start_health
                            self.falling_state = Fighter.FallingState.GETTING_UP
                            self.frame = 0
                            self.stamina = self.max_stamina
                            self.use_die_animation = False
                        else:
                            self.died()

        elif self.falling_state == Fighter.FallingState.GETTING_UP:
            self.frame += 1
            self.vpos.x += 0.1 * self.facing_x
            if self.frame > 20:
                self.falling_state = Fighter.FallingState.STANDING
                self.frame = 0

        elif self.falling_state == Fighter.FallingState.THROWN:
            self.frame += 1
            if self.height_above_ground <= 0:
                self.falling_state = Fighter.FallingState.FALLING
                self.frame = 80

        elif self.hit_timer > 0:
            self.hit_timer -= 1

        elif self.pickup_animation is not None:
            self.frame += 1
            if self.frame > 30:
                self.pickup_animation = None

        elif self.override_walking():
            pass

        elif self.falling_state == Fighter.FallingState.STANDING:
            if self.stamina < self.max_stamina:
                self.stamina += 1

            if self.weapon is not None:
                self.weapon.vpos = self.vpos + Vector2(self.facing_x * 20, 0)

            last_attack_recovery_time = 0 if not self.last_attack else self.last_attack.recovery_time

            if self.stamina <= 0:
                last_attack_recovery_time *= 3
            if self.attack_timer <= -last_attack_recovery_time:
                if self.weapon is None:
                    nearby_weapons = [weapon for weapon in game.weapons
                                      if (weapon.vpos - self.vpos).length() < 50]
                    if len(nearby_weapons) > 0:
                        if self.determine_pick_up_weapon():
                            dist = lambda weapon: (weapon.vpos - self.vpos).length_squared()
                            nearby_weapons.sort(key=dist)
                            for weapon in nearby_weapons:
                                if weapon.can_be_picked_up():
                                    self.pickup_animation = weapon.name
                                    self.frame = 0
                                    self.weapon = weapon
                                    weapon.pick_up(Fighter.WEAPON_HOLD_HEIGHT)
                                    break
                else:
                    if self.determine_drop_weapon():
                        self.drop_weapon()

                if self.pickup_animation is None:
                    attack = self.determine_attack()
                    if attack is not None:
                        self.log("Attack " + attack.sprite)
                        self.last_attack = attack
                        self.attack_timer = attack.anim_time
                        self.stamina -= attack.stamina_cost
                        self.stamina = max(self.stamina, MIN_STAMINA)
                        self.frame = 0

                        if attack.initial_sound is not None:
                            game.play_sound(*attack.initial_sound)

                        if attack.flying_kick:
                            self.vel.x = FLYING_KICK_VEL_X * self.facing_x
                            self.vel.y = FLYING_KICK_VEL_Y

                        if attack.grab:
                            game.player.grabbed()

            if self.attack_timer <= 0:
                desired_facing = self.get_desired_facing()
                if desired_facing is not None:
                    self.facing_x = desired_facing

                target = self.get_move_target()
                if target != self.vpos:
                    self.walking = True
                    self.vpos.x, dx = move_towards(self.vpos.x, target.x, self.speed.x)
                    self.vpos.y, dy = move_towards(self.vpos.y, target.y, self.speed.y)
                    self.apply_movement_boundaries(dx,dy)
                    self.frame += 1

                else:
                    self.walking = False
                    self.frame = 7
            else:
                self.frame += 1

                frame = self.get_attack_frame()
                if frame in self.last_attack.hit_frames:
                    if self.last_attack.throw:
                        if self.last_attack.grab:
                            if game.player.falling_state == Fighter.FallingState.GRABBED:
                                game.player.hit(self, self.last_attack)
                                game.player.thrown(self.facing_x)

                        elif self.weapon is not None:
                            self.weapon.throw(self.facing_x, self)
                            self.weapon = None

                    self.attack(self.last_attack)

    def attack(self, attack):
        if attack.strength > 0:
            for opponent in self.get_opponents():
                vec = opponent.vpos - self.vpos
                facing_correct = sign(self.facing_x) == sign(vec.x)
                if attack.rear_attack:
                    facing_correct = not facing_correct
                if abs(vec.y) < opponent.half_hit_area.y and facing_correct \
                        and abs(vec.x) < attack.reach + opponent.half_hit_area.x:
                            opponent.hit(self, attack)
                            if self.weapon is not None and self.weapon.is_broken():
                                self.drop_weapon()

    def hit(self, hitter, attack):
        if self.falling_state == Fighter.FallingState.STANDING \
                or self.falling_state == Fighter.FallingState.GRABBED:
                    if self.hit_timer <= 0:
                        self.stamina -= attack.strength * BASE_STAMINA_DAMAGE_MULTIPLIER \
                                * attack.stamina_damage_multiplier
                        self.stamina = max(self.stamina, MIN_STAMINA)
                        self.health -= attack.strength
                        self.hit_timer = attack.strength * 8 * attack.stun_time_multiplier
                        self.hit_frame = randint(0,1)

                        if self.attack_timer > 0 and (self.last_attack is not None 
                                                      and not self.last_attack.flying_kick):
                            self.attack_timer = 0

                        if self.weapon is not None:
                            self.drop_weapon()

                        if attack.hit_sound is not None:
                            game.play_sound(*attack.hit_sound)

                        if self.hit_sound is not None:
                            game.play_sound(self.hit_sound)

                        if (self.stamina <= 0 or self.health <= 0) and not isinstance(self, EnemyPortal):
                            self.falling_state = Fighter.FallingState.FALLING
                            self.frame = 0
                            self.hit_timer = 0

                            if self.health < 3:
                                self.health = 0
                                self.use_die_animation = (randint(0,1) == 0)

                        if isinstance(hitter, Fighter) and hitter.weapon is not None:
                            hitter.weapon.used()

                    if hitter.vpos.x != self.vpos.x:
                        self.facing_x = sign(hitter.vpos.x - self.vpos.x)

                        if self.falling_state == Fighter.FallingState.FALLING and not self.use_die_animation:
                            self.vel.x += -self.facing_x * 10

    def died(self):
        pass

    def draw(self, offset):
        self.image = self.determine_sprite()
        super().draw(offset)

        if DEBUG_SHOW_HEALTH_AND_STAMINA:
            text = f"HP: {self.health}\nSTM: {self.stamina}"
            screen.draw.text(text, fontsize=24, center=(self.x, self.y - 200), color="#FFFFFF", align="center")

        if DEBUG_SHOW_HIT_AREA_WIDTH:
            screen.draw.rect(Rect(self.x - self.half_hit_area.x, self.y - self.half_hit_area.y, self.half_hit_area.x * 2, self.half_hit_area.y * 2), (255,255,255))

        if DEBUG_SHOW_LOGS:
            y = self.y
            for l in reversed(self.logs):
                screen.draw.text(l, fontsize=14, center=(self.x, y), color="#FFFFFF", align="center")
                y += 10

    def determine_sprite(self):
        show = True

        if self.falling_state == Fighter.FallingState.FALLING:
            if self.frame > 60 and self.health <= 0 and (self.frame // 10) % 2 == 0:
                show = False

            if show:
                if self.just_knocked_off_scooter:
                    if self.frame > 10:
                        self.just_knocked_off_scooter = False
                        game.scooters.append(Scooter(self.vpos, self.facing_x,
                                                     self.color_variant))
                if self.just_knocked_off_scooter:
                    anim_type = "knocked_off"
                    frame = 0
                elif self.use_die_animation:
                    anim_type = "die"
                    frame = min(self.frame // 20, 2)
                else:
                    last_frame = 3 if isinstance(self, EnemyScooterboy) else 2
                    anim_type = "knockdown"
                    frame = min(self.frame // 10, last_frame)

        elif self.falling_state == Fighter.FallingState.GETTING_UP:
            anim_type = "getup"
            frame = min(self.frame // 10, 1)

        elif self.falling_state == Fighter.FallingState.GRABBED:
            show = False

        elif self.falling_state == Fighter.FallingState.THROWN:
            anim_type = "thrown"
            frame = min(self.frame // 12, 3)

        elif self.hit_timer > 0:
            frame = self.hit_frame
            anim_type = "hit"

        elif self.pickup_animation is not None:
            frame = min(self.frame // 12, self.weapon.end_pickup_frame)
            anim_type = f"pickup_{self.pickup_animation}"

        elif self.attack_timer > 0:
            anim_type = self.last_attack.sprite
            frame = self.get_attack_frame()

        else:
            if self.walking:
                anim_type = "walk"
                frame = (self.frame // self.anim_update_rate) % 4
            else:
                frame = 0
                anim_type = "walk" if self.weapon is not None else "stand"
            anim_type += ("_" + self.weapon.name) if self.weapon is not None else ""

        if show:
            facing_id = 1 if self.facing_x == 1 else 0
            image = f"{self.sprite}_{anim_type}_{facing_id}_{frame}"
            if self.color_variant is not None:
                image += "_" + str(self.color_variant)
        else:
            image = "blank"

        return image

    def get_attack_frame(self):
        frame = (self.frame // self.last_attack.frame_time)
        return min(frame, self.last_attack.frames - 1)

    def override_walking(self):
        return False

    def drop_weapon(self):
        self.pickup_animation = None
        self.weapon.dropped()
        self.weapon = None

    def grabbed(self):
        self.log("Grabbed")
        self.falling_state = Fighter.FallingState.GRABBED
        if self.weapon is not None:
            self.drop_weapon()

    def thrown(self, dir_x):
        self.log("Thrown")
        self.falling_state = Fighter.FallingState.THROWN
        self.vel.x = dir_x * PLAYER_THROW_VEL_X
        self.vel.y = PLAYER_THROW_VEL_Y
        self.facing_x = -dir_x
        self.vpos.x += dir_x * 50
        self.height_above_ground = 45

    def apply_movement_boundaries(self, dx, dy):
        if dx < 0 and self.vpos.x < game.boundary.left:
            self.vpos.x = game.boundary.left
        elif dx > 0 and self.vpos.x > game.boundary.right:
            self.vpos.x = game.boundary.right
        if dy < 0 and self.vpos.y < game.boundary.top:
            self.vpos.y = game.boundary.top
        elif dy > 0 and self.vpos.y > game.boundary.bottom:
            self.vpos.y = game.boundary.bottom

    @abstractmethod
    def determine_attack(self):
        pass

    @abstractmethod
    def determine_pick_up_weapon(self):
        pass

    @abstractmethod
    def determine_drop_weapon(self):
        pass

    @abstractmethod
    def get_opponents(self):
        pass

    @abstractmethod
    def get_move_target(self):
        pass

    @abstractmethod
    def get_desired_facing(self):
        pass

class Player(Fighter):
    def __init__(self, controls):
        super().__init__(pos=(400,400), anchor=("center",256), speed=Vector2(3,2),
                         sprite="hero", health=30, lives=3, separate_shadow=True)
        self.controls = controls
        self.extra_life_timer = 0

    def update(self):
        super().update()

        self.extra_life_timer -= 1

        for powerup in game.powerups:
            if (powerup.vpos - self.vpos).length() < 30:
                powerup.collect(self)

    def draw(self, offset):
        super().draw(offset)
        # screen.draw.text(f"{self.vpos}", (0,0))
        # screen.draw.text(f"{self.vpos}", self.pos)

    def determine_attack(self):
        if self.weapon is not None:
            if self.pickup_animation is None and self.controls.button_pressed(0):
                return ATTACKS[self.weapon.name]

        elif self.controls.button_pressed(0):
            if self.last_attack is not None and self.last_attack.combo_next is not None \
                    and self.attack_timer >= -30:
                        if 0 in self.last_attack.combo_next:
                            return ATTACKS[self.last_attack.combo_next[0]]
            return ATTACKS["punch"]

        elif self.controls.button_pressed(1):
            return choice((ATTACKS["kick"], ATTACKS["highkick"]))

        elif self.controls.button_pressed(2):
            return ATTACKS["elbow"]

        elif self.controls.button_pressed(3):
            return ATTACKS["flyingkick"]

        return None

    def determine_pick_up_weapon(self):
        return self.controls.button_pressed(0)

    def determine_drop_weapon(self):
        return self.weapon is not None and self.controls.button_pressed(1)

    def get_opponents(self):
        return game.enemies

    def get_move_target(self):
        return self.vpos + Vector2(self.controls.get_x() * self.speed.x,
                                   self.controls.get_y() * self.speed.y)

    def get_desired_facing(self):
        dx = self.controls.get_x()
        if dx != 0:
            self.facing_x = sign(dx)
        else:
            return self.facing_x

    def get_draw_order_offset(self):
        return 1

    def gain_extra_life(self):
        self.lives += 1
        self.extra_life_timer = 30

class Enemy(Fighter, ABC):
    class State(Enum):
        APPROACH_PLAYER = 0
        GO_TO_POS = 1
        GO_TO_WEAPON = 2
        PAUSE = 3
        KNOCKED_DOWN = 4
        RIDING_SCOOTER = 5
        PORTAL = 6
        PORTAL_EXPLODE = 7

    def __init__(self, pos, name, attacks, start_timer,
                 speed=Vector2(1,1), 
                 health=15, 
                 stamina=500,
                 approach_player_distance=ENEMY_APPROACH_PLAYER_DISTANCE,
                 anchor_y=256, 
                 half_hit_area=Vector2(25,20),
                 color_variant=None, 
                 hit_sound=None,
                 score=10):
        super().__init__(pos, ("center", anchor_y), speed=speed, sprite=name,
                         health=health, stamina=stamina, anim_update_rate=14,
                         half_hit_area=half_hit_area, color_variant=color_variant,
                         hit_sound=hit_sound)
        self.target = Vector2(self.vpos)
        self.target_weapon = None
        self.state = Enemy.State.PAUSE
        self.state_timer = start_timer
        self.attacks = attacks
        self.approach_player_distance = approach_player_distance
        self.score = score

    def spawned(self):
        pass

    def update(self):
        if self.state == Enemy.State.APPROACH_PLAYER:
            player = game.player

            if player.attack_timer > 0 \
                    and abs(self.vpos.y - player.vpos.y) < 20 \
                    and abs(self.vpos.x - player.vpos.x) < 200 \
                    and randint(0,500) == 0:
                        self.log("Back away from attack")
                        self.target.x = self.vpos.x - self.facing_x * 90
                        self.state = Enemy.State.GO_TO_POS
            else:
                if isinstance(self.weapon, Barrel):
                    x_offset = ENEMY_APPROACH_PLAYER_DISTANCE_BARREL
                else:
                    x_offset = self.approach_player_distance
                self.target.x = player.vpos.x + (x_offset * sign(self.vpos.x - player.vpos.x))
                self.target.y = player.vpos.y

        elif self.state == Enemy.State.GO_TO_POS:
            if self.target == self.vpos:
                self.make_decision()

        elif self.state == Enemy.State.GO_TO_WEAPON:
            if not self.target_weapon.can_be_picked_up() or not self.target_weapon.on_screen():
                self.target_weapon = None
                self.make_decision()
            else:
                self.target = Vector2(self.target_weapon.vpos)
                if self.target == self.vpos:
                    self.log("Pick up weapon")
                    self.pickup_animation = self.target_weapon.name
                    self.frame = 0
                    self.target_weapon.pick_up(Fighter.WEAPON_HOLD_HEIGHT)
                    self.weapon = self.target_weapon
                    self.target_weapon = None
                    self.make_decision()

        elif self.state == Enemy.State.PAUSE:
            self.state_timer -= 1
            if self.state_timer < 0:
                self.make_decision()

        elif self.state == Enemy.State.KNOCKED_DOWN:
            if self.falling_state == Fighter.FallingState.STANDING:
                self.make_decision()

        if self.state == Enemy.State.APPROACH_PLAYER \
                or self.state == Enemy.State.GO_TO_POS \
                or self.state == Enemy.State.GO_TO_WEAPON:
                    self.target.x = max(self.target.x, game.boundary.left)
                    self.target.x = min(self.target.x, game.boundary.right)
                    self.target.y = max(self.target.y, game.boundary.top)
                    self.target.y = min(self.target.y, game.boundary.bottom)
                    other_enemies_same_target = [enemy for enemy in game.enemies
                                                 if enemy is not self
                                                 and (enemy.target - self.target).length() < 20]
                    if len(other_enemies_same_target) > 0:
                        self.log("Same target")
                        self.make_decision()

        super().update()

    def draw(self, offset):
        super().draw(offset)

        if DEBUG_SHOW_TARGET_POS:
            screen.draw.line(self.vpos - offset, self.target - offset, (255,255,255))

    def determine_attack(self):
        px, py = game.player.vpos
        holding_barrel = isinstance(self.weapon, Barrel)

        if self.state == Enemy.State.APPROACH_PLAYER and game.player.FallingState ==\
                Fighter.FallingState.STANDING and self.vpos.y == p.y \
                and (self.approach_player_distance * 0.9 < abs(self.vpos.x - px) 
                     <= self.approach_player_distance * 1.1 or holding_barrel) \
                             and randint(0,19) == 0:
                                 if self.weapon is not None:
                                     return ATTACKS[self.weapon.name]
                                 else:
                                     chosen_attack = ATTACKS[choice(self.attacks)]
                                     if chosen_attack.grab and game.player.last_attack is not None \
                                             and game.player.last_attack.flying_kick:
                                                 return None
                                     return chosen_attack

    def determine_pick_up_weapon(self):
        return False

    def determine_drop_weapon(self):
        return False

    def get_opponents(self):
        return [game.player]

    def get_move_target(self):
        if self.target is None:
            return self.vpos
        else:
            return self.target

    def get_desired_facing(self):
        if self.state == Enemy.State.RIDING_SCOOTER:
            return self.facing_x
        else:
            return 1 if self.vpos.x < game.player.vpos.x else -1

    def hit(self, hitter, attack):
        if self.state == Enemy.State.KNOCKED_DOWN:
            return

        super().hit(hitter, attack)

        if self.state == Enemy.State.RIDING_SCOOTER:
            self.falling_state = Fighter.FallingState.FALLING
            self.frame = 0
            self.hit_timer = 0
            self.just_knocked_off_scooter = True

        if self.falling_state == Fighter.FallingState.FALLING:
            self.state = Enemy.State.KNOCKED_DOWN
            self.log("Knocked down")

    def make_decision(self):
        player = game.player

        if len(game.enemies) == 1:
            self.log("Only enemy, go to player")
            self.state = Enemy.State.APPROACH_PLAYER
        else:
            r = randint(0,9)
            if r < 7:
                other_enemies_on_same_side_attacking = [enemy for enemy in game.enemies
                                                        if enemy is not self
                                                        and enemy.state == Enemy.State.APPROACH_PLAYER
                                                        and sign(enemy.vpos.x-player.vpos.x)
                                                        == sign(self.vpos.x-player.vpos.x)]
                if len(other_enemies_on_same_side_attacking) > 0:
                    self.log("Begin flanking (same target)")
                    self.state = Enemy.State.GO_TO_POS
                    self.target.x = player.vpos.x - sign(self.vpos.x - player.vpos.x) * 50
                    self.target.y = player.vpos.y - sign(self.vpos.y - player.vpos.y) * 50
                    if self.target.y == player.vpos.y:
                        self.target.y = player.vpos.y + choice((-1,1)) * 50
                else:
                    self.log("Go to player")
                    self.state = Enemy.State.APPROACH_PLAYER

            elif r < 9:
                self.log("Go to distance from player")
                x_side = sign(self.vpos.x - player.vpos.x)
                if x_side == 0:
                    x_side = choice((1,-1))
                x1 = int(player.vpos.x + (150 * x_side))
                x2 = int(player.vpos.x + (400 * x_side))
                x = randint(min(x1,x2), max(x1,x2))
                y = randint(game.boundary.top, game.boundary.bottom)
                self.target = Vector2(x,y)
                self.state = Enemy.State.GO_TO_POS

            else:
                self.log("Pause")
                self.state_timer = randint(50, 100)
                self.state = Enemy.State.PAUSE

class EnemyVax(Enemy):
    def __init__(self, pos, start_timer=20):
        attacks = ("vax_lpunch", "vax_rpunch", "vax_pound")
        super().__init__(pos, "vax", attacks, start_timer=start_timer,
                         color_variant=randint(0,2), score=20)

class EnemyHoodie(Enemy):
    def __init__(self, pos, start_timer=20):
        attacks = ("hoodie_lpunch", "hoodie_rpunch", "hoodie_special")
        super().__init__(pos, "hoodie", attacks, health=12, speed=Vector2(1.2,1),
                         start_timer=start_timer, color_variant=randint(0,2), score=20)

    def died(self):
        super().died()
        if randint(0,2) == 0:
            game.weapons.append(Stick(self.vpos))

class EnemyScooterboy(Enemy):
    SCOOTER_SPEED_SLOW = 4
    SCOOTER_SPEED_FAST = 12
    SCOOTER_ACCELERATION = 0.2

    def __init__(self, pos, start_timer=20):
        attacks = ("scooterboy_attack1")
        super().__init__(pos, "scooterboy", attacks, start_timer=start_timer,
                         approach_player_distance=ENEMY_APPROACH_PLAYER_DISTANCE_SCOOTERBOY,
                         color_variant=randint(0,2), score=30)
        self.state = Enemy.State.RIDING_SCOOTER
        self.scooter_speed = EnemyScooterboy.SCOOTER_SPEED_SLOW
        self.scooter_target_speed = self.scooter_speed
        self.scooter_sound_channel = None

    def spawned(self):
        super().spawned()
        try:
            self.scooter_sound_channel = pygame.mixer.find_channel()
            if self.scooter_sound_channel is not None:
                self.scooter_sound_channel.play(game.get_sound("scooter_slow"), loops=-1, fade_ms=200)
        except Exception as e:
            pass

    def make_decision(self):
        if self.state != Enemy.State.RIDING_SCOOTER:
            super().make_decision()

    def determine_sprite(self):
        if self.state == Enemy.State.RIDING_SCOOTER:
            facing_id = 1 if self.facing_x == 1 else 0
            frame = 0
            if self.scooter_speed < self.scooter_target_speed:
                frame = min(self.frame // 5, 2)
            return f"{self.sprite}_ride_{facing_id}_{frame}_{self.color_variant}"
        else:
            return super().determine_sprite()

    def update(self):
        if self.state == Enemy.State.RIDING_SCOOTER:
            player = game.player

            if self.scooter_sound_channel is not None:
                left_vol = remap_clamp(abs(self.vpos.x - player.vpos.x+500), 0, 1000, 1, 0)
                right_vol = remap_clamp(abs(self.vpos.x - player.vpos.x-500), 0, 1000, 1, 0)
                self.scooter_sound_channel.set_volume(left_vol, right_vol)

            if self.scooter_speed != self.scooter_target_speed:
                self.scooter_speed, _ = move_towards(self.scooter_speed, 
                                                     self.scooter_target_speed,
                                                     EnemyScooterboy.SCOOTER_ACCELERATION)
                self.frame += 1
            elif self.on_screen() and randint(0,30) == 0:
                self.scooter_target_speed = EnemyScooterboy.SCOOTER_SPEED_FAST
                if self.scooter_sound_channel is not None:
                    self.scooter_sound_channel.play(game.get_sound("scooter_accelerate",6),
                                                    loops=0, fade_ms=200)
                    self.frame = 0

            self.target.x = self.vpos.x + self.facing_x * self.scooter_speed
            self.vpos.x = self.target.x

            if (self.facing_x > 0 and self.x > WIDTH + 200) or (self.facing_x < 0 and self.x < -200):
                self.facing_x = -self.facing_x
                self.target.y = player.vpos.y

                if game.player.falling_state == Fighter.FallingState.STANDING:
                    self.vpos.y = self.target.y
                else:
                    while abs(self.vpos.y - self.target.y) < 40:
                        self.vpos.y = randint(MIN_WALK_Y, HEIGHT-1)

                self.scooter_target_speed = EnemyScooterboy.SCOOTER_SPEED_SLOW
                self.scooter_speed = self.scooter_target_speed

                if self.scooter_sound_channel is not None:
                    self.scooter_sound_channel.play(game.get_sound("scooter_slow"), loops=1, fade_ms=200)

            if player.falling_state == Fighter.FallingState.STANDING \
                    and abs(player.vpos.y - self.vpos.y) < 30 \
                    and abs(self.vpos.x - player.vpos.x) < 60 \
                    and player.height_above_ground < 20:
                        player.hit(self, ATTACKS["scooter_hit"])

        elif self.just_knocked_off_scooter and self.scooter_sound_channel is not None \
                and self.scooter_sound_channel.get_busy():
                    self.scooter_sound_channel.stop()

        super().update()

    def override_walking(self):
        return self.state == Enemy.State.RIDING_SCOOTER

    def died(self):
        super().died()

        if randint(0,19) == 0:
            game.weapons.append(Chain(self.vpos))

        if self.scooter_sound_channel is not None and self.scooter_sound_channel.get_busy():
            self.scooter_sound_channel.stop()

class EnemyBoss(Enemy):
    def __init__(self, pos, start_timer=20):
        boss_attacks = ("boss_lpunch", "boss_rpunch", "boss_kick", "boss_grab_player",)
        super().__init__(pos, "boss", boss_attacks, speed=Vector2(0.9,0.8), health=25,
                         stamina=1000, start_timer=start_timer, anchor_y=280,
                         half_hit_area=Vector2(30,20), color_variant=randint(0,2),
                         score=75)

    def make_decision(self):
        if self.weapon is None:
            available_barrels = [weapon for weapon in game.weapons if isinstance(weapon, Barrel)
                                 and weapon.can_be_picked_up() and weapon.on_screen()]
            if len(available_barrels) > 0:
                for weapon in available_barrels:
                    other_enemies_same_target = [enemy for enemy in game.enemies
                                                 if enemy is not self
                                                 and enemy.target_weapon is weapon]
                    if len(other_enemies_same_target) == 0:
                        self.log("Go to weapon")
                        self.state = Enemy.State.GO_TO_WEAPON
                        self.target_weapon = weapon
                        return

        super().make_decision()

class EnemyPortal(Enemy):
    GENERATE_ANIMATION_FRAMES = 6
    GENERATE_ANIMATION_DIVISOR = 16
    GENERATE_ANIMATION_TIME = GENERATE_ANIMATION_FRAMES * GENERATE_ANIMATION_DIVISOR

    def __init__(self, pos, enemies, spawn_interval, spawn_interval_change=0,
                 max_spawn_interval=600, max_enemies=5, start_timer=90):
        super().__init__(pos, "portal", (), start_timer=start_timer, anchor_y=340,
                         half_hit_area=Vector2(50,50), hit_sound="portal_hit")
        self.enemies = enemies
        self.spawn_interval = spawn_interval
        self.spawn_timer = spawn_interval
        self.spawn_interval_change = spawn_interval_change
        self.max_spawn_interval = max_spawn_interval
        self.max_enemies = max_enemies
        self.spawning_enemy = None
        self.spawn_facing = 0

    def spawned(self):
        super().spawned()
        game.play_sound("portal_appear")

    def make_decision(self):
        self.state = Enemy.State.PORTAL

    def determine_sprite(self):
        if self.state == Enemy.State.PAUSE and self.frame // 8 < 4:
            return "portal_grow_" + str(min(self.frame // 8, 3))

        elif self.state == Enemy.State.PORTAL_EXPLODE:
            return "portal_destroyed_" + str(min(self.frame // 6, 7))

        elif self.spawning_enemy is not None:
            frame = self.frame // EnemyPortal.GENERATE_ANIMATION_DIVISOR
            if frame < 3:
                return "portal_generate_" + str(frame)
            else:
                frame = min(frame - 3, 2)
                sprite = self.spawning_enemy.sprite
                col = self.spawning_enemy.color_variant
                return f"portal_generate_{sprite}_{self.spawn_facing}_{frame}_{col}"

        elif self.hit_timer > 0:
            return "portal_hit_0"

        else:
            return "portal_idle_" + str((self.frame // 8) % 8)

    def update(self):
        self.frame += 1

        if self.state == Enemy.State.PORTAL:
            if self.health <= 0:
                self.state = Enemy.State.PORTAL_EXPLODE
                self.frame = 0
                game.play_sound("portal_destroyed")
            else:
                self.spawn_timer -= 1
                if self.spawn_timer <= 0 and self.spawning_enemy is not None:
                    game.spawn_enemy(self.spawning_enemy)

                    self.spawning_enemy = None

                    self.spawn_interval += self.spawn_interval_change
                    self.spawn_interval = min(self.spawn_interval, self.max_spawn_interval)
                    self.spawn_timer = self.spawn_interval

                elif self.spawning_enemy is None and self.spawn_timer <= EnemyPortal.GENERATE_ANIMATION_TIME:
                    if len(game.enemies) >= self.max_enemies:
                        self.spawn_timer = 60
                    else:
                        chosen_enemy = choice(self.enemies)
                        self.spawn_facing = 0 if self.vpos.x > game.player.vpos.x else 1
                        self.spawning_enemy = chosen_enemy(self.vpos)
                        self.frame = 0
                        game.play_sound("portal_enemy_spawn")

        elif self.state == Enemy.State.PORTAL_EXPLODE:
            if self.frame > 50:
                self.lives -= 1
                self.died()

        super().update()

    def override_walking(self):
        return True

class Scooter(ScrollHeightActor):
    def __init__(self, pos, facing_x, color_variant):
        super().__init__("blank", pos, ("center",256))
        self.facing_x = facing_x
        self.color_variant = color_variant
        self.vel_x = -facing_x * 8
        self.frame = 0
        game.play_sound("scooter_fall")

    def update(self):
        self.frame += 1
        self.vpos.x += self.vel_x
        self.vel_x *= 0.94
        facing_id = 1 if self.facing_x > 0 else 0
        self.image = f"scooterboy_bike_{facing_id}_{min(self.frame//30,2)}_{self.color_variant}"

    def get_draw_order_offset(self):
        return -1

class Weapon(ScrollHeightActor):
    def __init__(self, name, sprite, pos, end_pickup_frame, anchor=ANCHOR_CENTER,
                 bounciness=0, ground_friction=0.5, air_friction=0.996, separate_shadow=False):
        super().__init__(sprite, pos, anchor=anchor, separate_shadow=separate_shadow)
        self.name = name
        self.end_pickup_frame = end_pickup_frame
        self.held = False
        self.vel = Vector2(0,0)
        self.bounciness = bounciness
        self.ground_friction = ground_friction
        self.air_friction = air_friction

    def update(self):
        if not self.held:
            if self.height_above_ground > 0 or self.vel.y != 0:
                self.vel.y += WEAPON_GRAVITY
                if self.vel.y > self.height_above_ground:
                    if self.bounciness > 0 and self.vel.y > 1:
                        self.height_above_ground = abs(self.height_above_ground - self.vel.y) * self.bounciness
                        self.vel.y = -self.vel.y * self.bounciness
                    else:
                        self.height_above_ground = 0
                        self.vel.y = 0
                else:
                    self.height_above_ground -= self.vel.y

                assert(self.height_above_ground >= 0)

            self.vpos.x += self.vel.x

            friction = self.ground_friction if self.height_above_ground == 0 else self.air_friction

            self.vel.x *= friction
            if abs(self.vel.x) < 0.05:
                self.vel.x = 0

    def can_be_picked_up(self):
        return not self.held and self.height_above_ground == 0

    def pick_up(self, hold_height):
        assert(not self.held)
        self.held = True
        self.height_above_ground = hold_height
        self.vel = Vector2(0,0)
        self.image = "blank"

    def dropped(self):
        assert(self.held)
        self.held = False

    def used(self):
        pass

    def is_broken(self):
        return False

class Barrel(Weapon):
    def __init__(self, pos):
        super().__init__("barrel", "barrel_upright", pos, end_pickup_frame=2,
                         anchor=("center",190), bounciness=0.75, ground_friction=0.96,
                         separate_shadow=True)
        self.last_thrower = None
        self.frame = 0

    def update(self):
        super().update()

        if not self.held and not self.can_be_picked_up() and self.vel.x != 0:
            for fighter in [game.player] + game.enemies:
                BARREL_HEIGHT = 40
                fighter_bottom_height = fighter.height_above_ground
                barrel_bottom_height = self.height_above_ground - (BARREL_HEIGHT // 2)
                barrel_top_height = barrel_bottom_height + BARREL_HEIGHT

                if fighter is not self.last_thrower \
                        and fighter.falling_state == Fighter.FallingState.STANDING \
                        and abs(fighter.vpos.y - self.vpos.y) < 30 \
                        and abs(self.vpos.x - fighter.vpos.x) < 30 \
                        and fighter_bottom_height < barrel_top_height:
                            fighter.hit(self, ATTACKS["barrel"])

            facing_id = 1 if self.vel.x > 0 else 0
            self.frame += 1
            self.image = f"barrel_roll_{facing_id}_{(self.frame // 14) % 4}"

    def throw(self, dir_x, thrower):
        self.dropped()
        self.vel.x = dir_x * BARREL_THROW_VEL_X
        self.vel.y = BARREL_THROW_VEL_Y
        self.last_thrower = thrower
        self.vpos.x += dir_x * 104

    def dropped(self):
        super().dropped()
        self.image = "barrel_roll_0_0"

    def can_be_picked_up(self):
        return super().can_be_picked_up() and self.vel.length() < 1

    def get_draw_order_offset(self):
        return 2

class BreakableWeapon(Weapon):
    def __init__(self, pos, name, durability):
        super().__init__(name, name, pos, end_pickup_frame=1, anchor=("center","center"))
        self.break_counter = durability

    def dropped(self):
        super().dropped()
        self.image = self.name

    def get_draw_order_offset(self):
        return -50

    def used(self):
        self.break_counter -= 1
        if self.break_counter == 0:
            self.on_break()

    def is_broken(self):
        return self.break_counter <= 0

    @abstractmethod
    def on_break(self):
        pass

class Stick(BreakableWeapon):
    def __init__(self, pos):
        super().__init__(pos, "stick", durability=randint(12, 16))

    def on_break(self):
        game.play_sound("stick_break")

class Chain(BreakableWeapon):
    def __init__(self, pos):
        super().__init__(pos, "chain", durability=randint(18, 25))

    def on_break(self):
        game.play_sound("chain_break")
    
class Powerup(ScrollHeightActor):
    def __init__(self, image, pos):
        super().__init__(pos, image)
        self.collected = False

    def update(self):
        pass

    @abstractmethod
    def collect(self, collector):
        self.collected = True

class HealthPowerup(Powerup):
    def __init__(self, pos):
        super().__init__(pos, "health_pickup")

    def collect(self, collector):
        super().collect(collector)
        collector.health = min(collector.health + 20, collector.start_health)
        game.play_sound("health", 1)

class ExtraLifePowerup(Powerup):
    def __init__(self, pos):
        super().__init__(pos, "ingame_life9")
        self.timer = 0

    def update(self):
        super().update()
        self.timer += 1
        self.image = "ingame_life" + str((self.timer // 2) % 10)

    def collect(self, collector):
        super().collect(collector)
        collector.gain_extra_life()
        game.play_sound("health", 1)

class Stage:
    def __init__(self, enemies, max_scroll_x, weapons=[], powerups=[]):
        self.enemies = enemies
        self.powerups = powerups
        self.max_scroll_x = max_scroll_x
        self.weapons = weapons

def setup_stages():
    global STAGES
    STAGES = (
            # Stage(max_scroll_x=0, enemies=[]),

            # Stage(max_scroll_x=200,
            #       enemies=[],
            #       #enemies=[EnemyScooterboy(pos=(200, 400))],
            #       #enemies=[EnemyPortal(pos=(600, 400), enemies=(EnemyVax, EnemyHoodie), spawn_interval=60, spawn_interval_change=30)],
            #       #enemies=[EnemyScooterboy(pos=(200, 400)),EnemyScooterboy(pos=(100, 300)),EnemyScooterboy(pos=(300, 600)),EnemyScooterboy(pos=(200, 500)),],
            #       #enemies=[EnemyVax(pos=(200, 400)),EnemyVax(pos=(100, 300)),EnemyVax(pos=(300, 600)),EnemyVax(pos=(200, 500)),],
            #       #enemies=[EnemyBoss(pos=(500, 380))],
            #       weapons=[Barrel((300, 400))]
            #       ),

            # Stage(max_scroll_x=250,
            #       #enemies=[EnemyScooterboy(pos=(200, 400))],
            #       enemies=[EnemyPortal(pos=(600, 400), enemies=(EnemyVax, EnemyHoodie), spawn_interval=120, spawn_interval_change=30, start_timer=300)],
            #       #enemies=[EnemyScooterboy(pos=(200, 400)),EnemyScooterboy(pos=(100, 300)),EnemyScooterboy(pos=(300, 600)),EnemyScooterboy(pos=(200, 500)),],
            #       #enemies=[EnemyBoss(pos=(500, 380))],
            #       weapons=[Barrel((300, 400))]
            #       ),

            Stage(max_scroll_x=300,
                  enemies=[EnemyVax(pos=(1000,400))],
                  #weapons=[Barrel((300, 400))],
                  #powerups=[HealthPowerup(pos=(1100, MIN_WALK_Y)), ExtraLifePowerup(pos=(1000, MIN_WALK_Y))]
                  ),

            Stage(max_scroll_x=600,
                  enemies=[EnemyVax(pos=(1400,400)),
                           EnemyHoodie(pos=(1500,500))],
                  weapons=[Barrel((1600, 400))]),

            Stage(max_scroll_x=600,
                  enemies=[EnemyScooterboy(pos=(200,400))]),

            Stage(max_scroll_x=900,
                  enemies=[EnemyBoss(pos=(1800,400)),
                           EnemyVax(pos=(400,400))]),

            Stage(max_scroll_x=1400,
                  enemies=[EnemyHoodie(pos=(2100,380)),
                           EnemyHoodie(pos=(2100,480)),
                           EnemyHoodie(pos=(800,420))],
                  powerups=[HealthPowerup(pos=(2300, MIN_WALK_Y))]
                  ),

            Stage(max_scroll_x=1900,
                  enemies=[EnemyVax(pos=(2400,380)),
                           EnemyHoodie(pos=(2500,480)),
                           EnemyScooterboy(pos=(2800,400))]),

            Stage(max_scroll_x=2500,
                  enemies=[EnemyScooterboy(pos=(3800,380)),
                           EnemyScooterboy(pos=(3300,480)),
                           EnemyScooterboy(pos=(1200,400))]),

            Stage(max_scroll_x=3000,
                  enemies=[EnemyVax(pos=(4000,380)),
                           EnemyVax(pos=(3900,480)),
                           EnemyVax(pos=(4200,460)),
                           EnemyVax(pos=(4200,450)),
                           EnemyHoodie(pos=(3900,300)),
                           EnemyHoodie(pos=(3950,320))]),

            Stage(max_scroll_x=3600,
                  enemies=[EnemyVax(pos=(4600,380)),
                           EnemyScooterboy(pos=(1200,350)),
                           EnemyScooterboy(pos=(1400,350)),
                           EnemyScooterboy(pos=(1600,350)),
                           EnemyScooterboy(pos=(1800,350)),
                           EnemyScooterboy(pos=(2000,350))],
                  powerups=[HealthPowerup(pos=(5100, MIN_WALK_Y))]
                  ),

            Stage(max_scroll_x=4600,
                  enemies=[EnemyHoodie(pos=(4800,380)),
                           EnemyHoodie(pos=(4800,350)),
                           EnemyScooterboy(pos=(1200,350)),
                           EnemyScooterboy(pos=(1400,350)),
                           EnemyScooterboy(pos=(4800,350)),
                           EnemyScooterboy(pos=(4800,400)),
                           EnemyScooterboy(pos=(4900,450))]),

            Stage(max_scroll_x=5500,
                  enemies=[EnemyBoss(pos=(6500,380)),
                           EnemyBoss(pos=(6500,360))],
                  weapons=[Barrel(pos=(6000, 400)),
                           Barrel(pos=(5900, 370))]),

            Stage(max_scroll_x=6400,
                  enemies=[EnemyBoss(pos=(7000,380)),
                           EnemyBoss(pos=(7000,360)),
                           EnemyBoss(pos=(7000,390))],
                  weapons=[Barrel(pos=(7000, 380))]),

            Stage(max_scroll_x=6900,
                  enemies=[EnemyVax(pos=(7500,380)),
                           EnemyScooterboy(pos=(7500,350)),
                           EnemyScooterboy(pos=(7500,360))]),

            Stage(max_scroll_x=7550,
                  enemies=[EnemyHoodie(pos=(8000,380), start_timer=50),
                           EnemyVax(pos=(8200,340), start_timer=100),
                           EnemyHoodie(pos=(8200,340), start_timer=150),
                           EnemyHoodie(pos=(7900,360), start_timer=200),
                           EnemyHoodie(pos=(8300,390), start_timer=250),
                           EnemyVax(pos=(8700,400), start_timer=300),
                           EnemyHoodie(pos=(8800,400), start_timer=400),
                           EnemyHoodie(pos=(8900,400), start_timer=500),
                           EnemyVax(pos=(9000,320), start_timer=600),
                           EnemyVax(pos=(9100,400), start_timer=700),
                           EnemyHoodie(pos=(9100,450), start_timer=800),
                           EnemyVax(pos=(9100,420), start_timer=900),
                           EnemyBoss(pos=(9100,450), start_timer=1000),
                           ],
                  powerups=[HealthPowerup(pos=(8000, MIN_WALK_Y)),
                            ExtraLifePowerup(pos=(8200, MIN_WALK_Y))]
                  ),

            Stage(max_scroll_x=8400,
                  enemies=[EnemyPortal(pos=(8900, 400), enemies=(EnemyVax, EnemyHoodie), spawn_interval=120, spawn_interval_change=30, max_spawn_interval=250, max_enemies=2),],
                  # weapons=[Barrel(pos=(9000,380)),
                  #          Barrel(pos=(8900,360))
                  ),

            Stage(max_scroll_x=8900,
                  enemies=[EnemyPortal(pos=(9500, 400), enemies=(EnemyVax, EnemyHoodie), spawn_interval=120, spawn_interval_change=50, max_spawn_interval=250, max_enemies=5),
                           EnemyPortal(pos=(9500, 400), enemies=(EnemyScooterboy,), spawn_interval=160, spawn_interval_change=50, max_spawn_interval=250, max_enemies=5),],
                  # weapons=[Barrel(pos=(9000,380)),
                  #          Barrel(pos=(8900,360))
                  ),

            Stage(max_scroll_x=9600,
                  enemies=[EnemyPortal(pos=(10000, 420), enemies=(EnemyVax, EnemyHoodie), spawn_interval=120, spawn_interval_change=50, max_spawn_interval=250, max_enemies=5),
                           EnemyScooterboy(pos=(10500,320)),
                           EnemyScooterboy(pos=(10500,350)),
                           EnemyScooterboy(pos=(10500,380)),
                           ],
                  # weapons=[Barrel(pos=(9000,380)),
                  #          Barrel(pos=(8900,360))
                  ),

            Stage(max_scroll_x=10800,
                  enemies=[EnemyPortal(pos=(11200, 420), enemies=(EnemyHoodie,), spawn_interval=40, spawn_interval_change=10, max_spawn_interval=250, max_enemies=8),
                           ],
                  # weapons=[Barrel(pos=(9000,380)),
                  #          Barrel(pos=(8900,360))
                  ),

            Stage(max_scroll_x=11400,
                  enemies=[EnemyPortal(pos=(12100, 340), enemies=(EnemyScooterboy,), spawn_interval=40, spawn_interval_change=20, max_spawn_interval=250, max_enemies=8),
                           EnemyPortal(pos=(11900, 400), enemies=(EnemyScooterboy,), spawn_interval=50, spawn_interval_change=25, max_spawn_interval=250, max_enemies=8),
                           ],
                  weapons=[Barrel(pos=(11800,380))],
                  powerups=[HealthPowerup(pos=(12000, MIN_WALK_Y)),
                            HealthPowerup(pos=(12500, MIN_WALK_Y))]
                  ),

            Stage(max_scroll_x=12600,
                  enemies=[EnemyPortal(pos=(12900, 340), enemies=(EnemyBoss,), spawn_interval=240, spawn_interval_change=20, max_spawn_interval=300, max_enemies=4),
                           EnemyHoodie(pos=(13200,320)),
                           EnemyHoodie(pos=(13200,330)),
                           EnemyVax(pos=(13400,360)),
                           ],
                  ),

            Stage(max_scroll_x=13400,
                  enemies=[EnemyPortal(pos=(13600, 320), enemies=(EnemyVax,), spawn_interval=230, spawn_interval_change=20, max_spawn_interval=300, max_enemies=10),
                           EnemyPortal(pos=(13600, 435), enemies=(EnemyHoodie,), spawn_interval=240, spawn_interval_change=20, max_spawn_interval=300, max_enemies=10),
                           EnemyPortal(pos=(14000, 320), enemies=(EnemyScooterboy,), spawn_interval=250, spawn_interval_change=30, max_spawn_interval=300, max_enemies=10),
                           EnemyPortal(pos=(14000, 435), enemies=(EnemyBoss,), spawn_interval=260, spawn_interval_change=30, max_spawn_interval=300, max_enemies=10),
                          ],
                  ),

            Stage(max_scroll_x=14700,
                  enemies=[EnemyPortal(pos=(14900, 320), enemies=(EnemyVax,), spawn_interval=220, spawn_interval_change=20, max_spawn_interval=300, max_enemies=8),
                           EnemyPortal(pos=(14900, 435), enemies=(EnemyHoodie,), spawn_interval=230, spawn_interval_change=20, max_spawn_interval=300, max_enemies=8),
                           EnemyPortal(pos=(15300, 320), enemies=(EnemyScooterboy,), spawn_interval=240, spawn_interval_change=20, max_spawn_interval=300, max_enemies=8),
                           EnemyPortal(pos=(15300, 435), enemies=(EnemyBoss,), spawn_interval=250, spawn_interval_change=20, max_spawn_interval=300, max_enemies=8),
                          ],
                  powerups=[HealthPowerup(pos=(14650, 350)),]
                  ),

            Stage(max_scroll_x=15400,
                  enemies=[EnemyPortal(pos=(15800, 350), enemies=(EnemyVax,EnemyHoodie,EnemyScooterboy), spawn_interval=60, spawn_interval_change=20, max_spawn_interval=300, max_enemies=8),
                          ],
                  powerups=[HealthPowerup(pos=(16000, MIN_WALK_Y)),]
                  ),

            Stage(max_scroll_x=16600,
                  enemies=[EnemyVax(pos=(17600,300)),
                           EnemyVax(pos=(17900,320)),
                           EnemyVax(pos=(17600,340)),
                           EnemyVax(pos=(17900,360)),
                           EnemyVax(pos=(17600,380)),
                           EnemyVax(pos=(17900,400)),
                           EnemyVax(pos=(17600,420)),
                          ],
                  powerups=[HealthPowerup(pos=(17000, MIN_WALK_Y)),],
                  weapons=[Barrel(pos=(17000,380))],
                  ),

            Stage(max_scroll_x=17400,
                  enemies=[EnemyBoss(pos=(17800,MIN_WALK_Y)),
                           EnemyScooterboy(pos=(18500,380)),
                           EnemyScooterboy(pos=(18600,380)),
                           EnemyScooterboy(pos=(18700,380)),
                           EnemyScooterboy(pos=(18800,380)),
                           EnemyScooterboy(pos=(19000,380)),
                          ],
                  weapons=[Stick(pos=(18000,340))],
                  ),

            Stage(max_scroll_x=18500,
                  enemies=[EnemyBoss(pos=(18800, 320)),
                           EnemyPortal(pos=(18900, 390), enemies=(EnemyVax, EnemyHoodie),
                                       start_timer=400, spawn_interval=30, spawn_interval_change=5, max_enemies=10),
                           ],
             ),

            Stage(max_scroll_x=19300,
                  enemies=[EnemyScooterboy(pos=(19900, 340))],
                  weapons=[Barrel(pos=(19400,340))],
                  powerups=[HealthPowerup(pos=(19600, MIN_WALK_Y)),],
             ),

            # Final battles

            Stage(max_scroll_x=20500,
                  enemies=[EnemyHoodie(pos=(20900, 380), start_timer=500),
                           EnemyBoss(pos=(21500,330)),
                           EnemyBoss(pos=(21500,350)),
                           EnemyBoss(pos=(21500,370)),
                           EnemyBoss(pos=(21500,390)),
                           EnemyBoss(pos=(18200,320)),
                           EnemyBoss(pos=(17800,390)),
                           ],
                  powerups=[ExtraLifePowerup(pos=(20900, MIN_WALK_Y))]),

            Stage(max_scroll_x=20500,
                  enemies=[EnemyPortal(pos=(20700, 315), enemies=(EnemyVax,), start_timer=600, spawn_interval=60, spawn_interval_change=5, max_enemies=20),
                           EnemyPortal(pos=(20700, 440), enemies=(EnemyHoodie,), start_timer=600, spawn_interval=60, spawn_interval_change=10, max_enemies=20),
                           EnemyPortal(pos=(21100, 315), enemies=(EnemyScooterboy,), start_timer=600, spawn_interval=60, spawn_interval_change=15, max_enemies=20),
                           EnemyPortal(pos=(21100, 440), enemies=(EnemyBoss,), start_timer=600, spawn_interval=60, spawn_interval_change=20, max_enemies=20),
                           ]),

            )

class Game:
    def __init__(self, controls=None):
        self.player = Player(controls)
        self.enemies = []
        self.weapons = []
        self.scooters = []
        self.powerups = []
        self.stage_index = -1
        self.timer = 0
        self.score = 0
        self.scroll_offset = Vector2(0,0)
        self.max_scroll_offset_x = 0
        self.scrolling = False
        self.boundary = Rect(0, MIN_WALK_Y, WIDTH-1, HEIGHT-MIN_WALK_Y)

        setup_stages()

        stolen_items = ("A SHIPMENT OF RASPBERRY\nPIS",
                        "YOUR COPY OF CODE THE\nCLASSICS VOL 2",
                        "THE COMPLETE WORKS OF\nSHAKESPEARE",
                        "THE BLOCKCHAIN",
                        "THE WORLD'S ENTIRE SUPPLY\nOF COVID VACCINES",
                        "ALL OF YOUR SAVED GAME\nFILES",
                        "YOUR DOG'S FLEA MEDICINE")

        self.text_active = INTRO_ENABLED

        self.intro_text = "THE NOTORIOUS CRIME BOSS\nEBEN UPTON HAS STOLEN\n" \
                + choice(stolen_items) \
                + "\n\n\nFIGHT TO RECLAIM WHAT\nHAS BEEN TAKEN!"

        self.outro_text = "FOLLOWING THE DEFEAT OF\nTHE EVIL GANG, HUMANITY\n" \
                "ENTERED A NEW GOLDEN AGE\nIN WHICH CRIME BECAME A\n" \
                "THING OF THE PAST. THE\nWORD ITSELF WAS SOON\n" \
                "FORGOTTEN AND EVERYONE\nHAD A BIG PARTY IN YOUR\n" \
                "HONOR.\n\nNICE JOB!"

        self.current_text = self.intro_text
        self.displayed_text = ""

    def next_stage(self):
        self.stage_index += 1
        if self.stage_index < len(STAGES):
            stage = STAGES[self.stage_index]
            self.max_scroll_offset_x = stage.max_scroll_x
            if self.scrolling or self.max_scroll_offset_x <= self.scroll_offset.x:
                self.create_stage_objects(stage)
        else:
            if not self.text_active:
                self.text_active = True
                self.current_text = self.outro_text
                self.displayed_text = ""
                self.timer = 0

    def check_won(self):
        return self.stage_index >= len(STAGES) and not self.text_active

    def create_stage_objects(self, stage):
        self.enemies = stage.enemies.copy()
        for enemy in self.enemies:
            enemy.spawned()

        self.weapons.extend(stage.weapons)
        self.powerups.extend(stage.powerups)

    def spawn_enemy(self, enemy):
        self.enemies.append(enemy)
        enemy.spawned()

    def update(self):
        if DEBUG_PROFILING:
            p = Profiler()

        self.timer += 1

        if self.text_active:
            if self.timer % 6 == 0 and len(self.displayed_text) < len(self.current_text):
                length_to_display = min(self.timer // 6, len(self.current_text))
                self.displayed_text = self.current_text[:length_to_display]
                if not self.displayed_text[-1].isspace():
                    self.play_sound("teletype")

            for button in range(4):
                if self.player.controls.button_pressed(button):
                    self.text_active = False
                    self.timer = 0

            return

        if DEBUG_SHOW_ATTACKS:
            debug_drawcalls.clear()

        for obj in [self.player] + self.enemies + self.weapons + self.scooters + self.powerups:
            obj.update()

        if self.scrolling:
            if self.scroll_offset.x < self.max_scroll_offset_x:
                diff = self.max_scroll_offset_x - self.scroll_offset.x
                scroll_speed = self.player.x / (WIDTH/4)
                scroll_speed = min(diff, scroll_speed)
                self.scroll_offset.x += scroll_speed
                self.boundary.left = self.scroll_offset.x
            else:
                self.scrolling = False
        else:
            begin_scroll_boundary = WIDTH - 300
            if self.player.vpos.x - self.scroll_offset.x > begin_scroll_boundary \
                    and self.scroll_offset.x < self.max_scroll_offset_x:
                        self.scrolling = True
                        if self.stage_index < len(STAGES):
                            stage = STAGES[self.stage_index]
                            self.create_stage_objects(stage)

        self.score += sum([enemy.score for enemy in self.enemies if enemy.lives <= 0])
        self.enemies = [enemy for enemy in self.enemies if enemy.lives > 0]
        self.scooters = [scooter for scooter in self.scooters if scooter.frame < 200]
        self.weapons = [weapon for weapon in self.weapons if not weapon.is_broken() and weapon.x > -200]
        self.powerups = [powerup for powerup in self.powerups if not powerup.collected and powerup.x > -200]

        if len(self.enemies) == 0 and self.scroll_offset.x == self.max_scroll_offset_x:
            self.next_stage()

        if DEBUG_PROFILING:
            print(f"update: {p.get_ms()}")

    def draw(self):
        self.draw_background()

        p = Profiler()
        all_objs = [self.player] + self.enemies + self.weapons + self.scooters + self.powerups
        all_objs.sort(key=lambda obj: obj.vpos.y + obj.get_draw_order_offset())
        for obj in all_objs:
            if obj:
                obj.draw(self.scroll_offset)
        if DEBUG_PROFILING:
            print("objs: {0}".format(p.get_ms()))

        p = Profiler()

        if self.scroll_offset.x < self.max_scroll_offset_x and (self.timer//30) % 2 == 0:
            screen.blit("arrow", (WIDTH-450,120))

        self.draw_ui()

        if DEBUG_PROFILING:
            print("icons: {0}".format(p.get_ms()))
            p = Profiler()

        if self.text_active or self.timer < 255:
            if self.text_active:
                alpha = 255
            else:
                alpha = max(0, 255 - self.timer)
            fullscreen_black_bmp.set_alpha(alpha)
            screen.blit(fullscreen_black_bmp, (0, 0))

        if self.text_active:
            draw_text(self.displayed_text, 50, 50)

        if DEBUG_SHOW_SCROLL_POS:
            screen.draw.text(f"{self.scroll_offset} {self.max_scroll_offset_x}", (0, 25))
            screen.draw.text(str(self.boundary.left), (0, 45))

        if DEBUG_SHOW_BOUNDARY:
            screen.draw.rect(Rect(self.boundary.left - self.scroll_offset.x, self.boundary.top, self.boundary.width, self.boundary.height), (255,255,255))

        for func in debug_drawcalls:
            func()

        if DEBUG_PROFILING:
            print("rest: {0}".format(p.get_ms()))

    def draw_ui(self):
        full_w = HEALTH_STAMINA_BAR_WIDTH
        full_h = HEALTH_STAMINA_BAR_HEIGHT

        health_w = int((game.player.health / game.player.start_health) * full_w)
        screen.surface.blit(getattr(images,"health"), (48,11), Rect(0,0,health_w,full_h))

        stam_w = int((game.player.stamina / game.player.max_stamina) * full_w)
        screen.surface.blit(getattr(images,"stamina"), (517,11), Rect(0,0,stam_w,full_h))

        screen.blit("status", (0,0))

        for i in range(game.player.lives):
            if game.player.extra_life_timer <= 0 or i < game.player.lives - 1:
                sprite_idx = 9
            else:
                sprite_idx = min(9, (30 - game.player.extra_life_timer) // 3)
            screen.blit("status_life" + str(sprite_idx), (i * 46 - 55, -35))

        draw_text(f"{self.score:04}", WIDTH // 2, 0, True)

    def draw_background(self):
        p = Profiler()
        road1_x = -(self.scroll_offset.x % WIDTH)
        road2_x = road1_x + WIDTH
        screen.blit("road",(road1_x, 0))
        screen.blit("road",(road2_x, 0))
        if DEBUG_PROFILING:
            print("road " + str(p.get_ms()))

        pos = -self.scroll_offset
        pos.x -= BACKGROUND_TILE_SPACING

        p = Profiler()
        for tile in BACKGROUND_TILES:
            if pos.x + 417 >= 0:
                screen.blit(tile, pos)
                pos.x += BACKGROUND_TILE_SPACING
                if pos.x >= WIDTH:
                    break
            else:
                pos.x += BACKGROUND_TILE_SPACING
        if DEBUG_PROFILING:
            print("bg " + str(p.get_ms()))

    def shutdown(self):
        for enemy in self.enemies:
            enemy.died()

    def get_sound(self, name, count=1):
        if self.player:
            return getattr(sounds, name + str(randint(0, count - 1)))

    def play_sound(self, name, count=1):
        if self.player:
            try:
                sound = self.get_sound(name, count)
                sound.play()
            except Exception as e:
                print(e)

def get_char_image_and_width(char):
    if char == " ":
        return None, 22
    else:
        if char in SPECIAL_FONT_SYMBOLS_INVERSE:
            image = getattr(images, SPECIAL_FONT_SYMBOLS_INVERSE[char])
        else:
            image = getattr(images, "font0" + str(ord(char)))
        return image, image.get_width()

def text_width(text):
    return sum([get_char_image_and_width(c)[1] for c in text])

def draw_text(text, x, y, center=False):
    if center:
        x -= text_width(text) // 2

    start_x = x

    for char in text:
        if char == "\n":
            y += 35
            x = start_x
        else:
            image, width = get_char_image_and_width(char)
            if image is not None:
                screen.blit(image, (x,y))
            x += width

def get_joystick_if_exists():
    return pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None

def setup_joystick_controls():
    global joystick_controls
    joystick = get_joystick_if_exists()
    joystick_controls = JoystickControls(joystick) if joystick is not None else None

def update_controls():
    keyboard_controls.update()
    if joystick_controls is None:
        setup_joystick_controls()
    if joystick_controls is not None:
        joystick_controls.update()

class State(Enum):
    TITLE = 1
    CONTROLS = 2
    PLAY = 3
    GAME_OVER = 4

def update():
    global state, game, total_frames

    total_frames += 1
    update_controls()

    def button_pressed_controls(button_num):
        for controls in (keyboard_controls, joystick_controls):
            if controls is not None and controls.button_pressed(button_num):
                return controls
        return None

    if state == State.TITLE:
        if button_pressed_controls(0) is not None:
            state = State.CONTROLS

    elif state == State.CONTROLS:
        controls = button_pressed_controls(0)
        if controls is not None:
            state = State.PLAY
            game = Game(controls)

    elif state == State.PLAY:
        game.update()
        if game.player.lives <= 0 or game.check_won():
            game.shutdown()
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        if button_pressed_controls(0) is not None:
            state = State.TITLE
            game = None

def draw():
    if state == State.TITLE:
        logo_img = images.title0 if total_frames // 20 % 2 == 0 else images.title1
        screen.blit(logo_img, (WIDTH//2 - logo_img.get_width() // 2,
                               HEIGHT//2 - logo_img.get_height() // 2))
        draw_text(f"PRESS {SPECIAL_FONT_SYMBOLS['xb_a']} OR Z",
                  WIDTH//2, HEIGHT - 50, True)

    elif state == State.CONTROLS:
        screen.fill((0,0,0))
        screen.blit("menu_controls", (0,0))

    elif state == State.PLAY:
        game.draw()

    elif state == State.GAME_OVER:
        img = images.status_win if game.check_won() else images.status_lose
        screen.blit(img, (WIDTH//2 - img.get_width() // 2,
                          HEIGHT//2 - img.get_height() // 2))

try:
    mixer.quit()
    mixer.init(44100, -16, 2, 1024)
    music.play("theme")
    music.set_volume(0.3)
except Exception as e:
    pass

total_frames = 0

keyboard_controls = KeyboardControls()
setup_joystick_controls()

state = State.TITLE
game = None

run()
