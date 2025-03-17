import sys
import math
from abc import ABC, abstractmethod
from enum import Enum, IntEnum
from random import randint, random, uniform, choice
import pygame
from pygame import surface, Vector2
from engine import *

if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

engine = sys.modules["engine"]
engine_version = [int(s) if s.isnumeric() else s
                  for s in engine.__version__.split('.')]

if engine_version < [1,1]:
    print(f"This game requires at least version 1.1 of the engine. "
          f"You are using version {engine.__version__}. Please upgrade.")
    sys.exit()

WIDTH, HEIGHT = 640, 640
TITLE = 'Brikz'

BAT_SPEED = 8
BAT_MIN_X, BAT_MAX_X = 35, 605
TOP_EDGE, RIGHT_EDGE, LEFT_EDGE = 50, 617, 23
BAT_TOP_EDGE = 590
BALL_INITIAL_OFFSET = 10
BALL_START_SPEED, BALL_MIN_SPEED, BALL_MAX_SPEED = 5, 4, 11
BALL_SPEED_UP_INTERVAL = 10 * 60
BALL_SPEED_UP_INTERVAL_FAST = 15 * 60
BALL_FAST_SPEED_THRESHOLD = 7
BALL_RADIUS = 7
BRICKS_X_START, BRICKS_Y_START = 20, 100
BRICK_WIDTH, BRICK_HEIGHT = 40, 20
SHADOW_OFFSET = 10
POWERUP_CHANCE = 0.2
BULLET_SPEED, FIRE_INTERVAL = 8, 30
PORTAL_ANIMATION_SPEED = 5

LEVELS = [
        ["        ",
         "        ",
         "        ",
         "     a  ",
         "    a7a ",
         "     a  ",
         "    a55 ",
         "    444 ",
         "   333a ",
         "  222a  ",
         " 111a   ",
         "   11aa ",
         "    111 ",
         "    6   ",
         "     6  "],

        ["        ",
         "        ",
         "    3   ",
         "    3   ",
         "    3   ",
         "    3000",
         "    3000",
         "   53000",
         "   53000",
         "  35a555",
         " 3 5aa55",
         "3  5aaa5",
         "  355555",
         "  333333",
         "   333  ",
         "    33  ",
         "     3  "],

        ["   7    ",
         "  77    ",
         " 7777   ",
         " 7777   ",
         " 77777  ",
         " 77777  ",
         " 77 777 ",
         " 7  7777",
         " 7   717",
         "     777",
         "      77",
         "      7 ",
         "     c7 ",
         "      c ",
         "      c "],

        ["   03   ",
         "   30   ",
         "    03  ",
         "    30  ",
         "     0  ",
         " 8   0  ",
         " 88 8033",
         "  883333",
         "   8333d",
         "   33733",
         "  33373d",
         " 3333333",
         " 3c 333d",
         " cc 3333",
         " c   3 3",
         "     3 3",
         "    3 3 ",
         "    c 3 ",
         "    cc3c",
         "    cccc",
         "      d "],

        ["5   9  0",
         "0   4  3",
         "08  4  4",
         "53  47 2",
         " 39 92 1",
         " 84  2  ",
         "  47 26 ",
         "5 92 71 ",
         "08 26 1 ",
         "53971 1 ",
         " 8471c6 ",
         "  926acc",
         "   71aad",
         "039 6aac",
         "dc421ac ",
         "  dccc  ",
         "    d   "],

        ["  dccccd",
         "  c89765",
         "  c34210",
         "  c34210",
         "  c34210",
         "  c34210",
         "  c3421d",
         "  c34210",
         "  c34210",
         "  c34210",
         "  c34210",
         "  c89765",
         "  dccccd"]
        ]

def get_mirrored_level(level):
    return [row + row[-2::-1] for row in level]

class Controls(ABC):
    def __init__(self):
        self.fire_previously_down = False
        self.is_fire_pressed = False

    def update(self):
        fire_down = self.fire_down()
        self.is_fire_pressed = fire_down and not self.fire_previously_down
        self.fire_previously_down = fire_down

    @abstractmethod
    def get_x(self):
        pass

    @abstractmethod
    def fire_down(self):
        pass

    def fire_pressed(self):
        return self.is_fire_pressed

class KeyboardControls(Controls):
    def get_x(self):
        if keyboard.left:
            return -BAT_SPEED
        elif keyboard.right:
            return BAT_SPEED
        else:
            return 0

    def fire_down(self):
        return keyboard.space

class JoystickControls(Controls):
    def __init__(self, joystick):
        super().__init__()
        self.joystick = joystick
        joystick.init()

    def get_x(self):
        if self.joystick.get_numhats() > 0 and self.joystick.get_hat(0)[0] != 0:
            return self.joystick.get_hat(0)[0] * BAT_SPEED

        axis_value = self.joystick.get_axis(0)
        if abs(axis_value) < 0.2:
            return 0
        else:
            return axis_value * BAT_SPEED

    def fire_down(self):
        if selfjoystick.get_numbuttons() <= 0:
            print("Warning: controller does not have any buttons!")
            return False
        return self.joystick.get_button(0) != 0

class AIControls(Controls):
    def __init__(self):
        super().__init__()
        self.offset = 0

    def get_x(self):
        if game.portal_active:
            return BAT_SPEED
        else:
            self.offset += randint(-1,1)
            self.offset = min(max(-40, self.offset), 40)
            return min(BAT_SPEED,
                       max(-BAT_SPEED, game.balls[0].x - (game.bat.x + self.offset)))

    def fire_down(self):
        return randint(0,5) == 0

class Powerup(IntEnum):
    EXTEND_BAT, GUN, SMALL_BAT, MAGNET, MULTI_BALL = 0, 1, 2, 3, 4
    FAST_BALLS, SLOW_BALLS, PORTAL, EXTRA_LIFE = 5, 6, 7, 8

class BatType(IntEnum):
    NORMAL, MAGNET, GUN, EXTENDED, SMALL = 0, 1, 2, 3, 4

POWERUP_BAT_TYPES = { 
                     Powerup.EXTEND_BAT: BatType.EXTENDED, Powerup.GUN: BatType.GUN,
                     Powerup.SMALL_BAT: BatType.SMALL, Powerup.MAGNET: BatType.MAGNET,
                     }

POWERUP_SOUNDS = {
        Powerup.EXTEND_BAT: "bat_extend", Powerup.GUN: "bat_gun",
        Powerup.MAGNET: "magnet", Powerup.SMALL_BAT: "bat_small",
        Powerup.EXTRA_LIFE: "extra_life", Powerup.FAST_BALLS: "speed_up",
        Powerup.SLOW_BALLS: "powerup", Powerup.MULTI_BALL: "multiball",
        }

class CollisionType(Enum):
    WALL, BAT, BAT_EDGE, BRICK, INDESTRUCTIBLE_BRICK = 0, 1, 2, 3, 4

class Bullet(Actor):
    def __init__(self, pos, side):
        super().__init__(f"bullet{side}", pos)
        self.alive = True

    def update(self):
        self.y -= BULLET_SPEED

        c = game.collide(self.x, self.y, Vector2(0, -1), 2)
        if c is not None:
            self.alive = False
            game.impacts.append(Impact(self.pos, 15))
            if c[2] == CollisionType.BRICK or c[2] == CollisionType.INDESTRUCTIBLE_BRICK:
                game.play_sound("bullet_hit", 4)

class Barrel(Actor):
    def __init__(self, pos):
        super().__init__("blank", pos)

        weights = {Powerup.EXTEND_BAT:6, Powerup.GUN:6, Powerup.SMALL_BAT:6,
                   Powerup.MAGNET:6, Powerup.MULTI_BALL:6, Powerup.FAST_BALLS:6,
                   Powerup.SLOW_BALLS:6, Powerup.EXTRA_LIFE:2,
                   Powerup.PORTAL:0 if game.bricks_remaining > 20 or game.portal_active else 20}

        types = [type_ for type_, weight in weights.items() for i in range(weight)]
        self.type = choice(types)
        self.time = 0
        self.shadow = Actor("barrels", (self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET))

    def update(self):
        self.time += 1
        self.y += 1

        w = (game.bat.width // 2) + BALL_RADIUS

        if self.y >= BAT_TOP_EDGE - 10 and self.y <= BAT_TOP_EDGE + 30 \
                and abs(self.x - game.bat.x) < w:
                    game.impacts.append(Impact((self.x, self.y - 11), 14))

                    if self.type in POWERUP_SOUNDS:
                        game.play_sound(POWERUP_SOUNDS[self.type])

                    self.y = HEIGHT + 100

                    if self.type in POWERUP_BAT_TYPES:
                        game.bat.change_type(POWERUP_BAT_TYPES[self.type])
                    elif self.type == Powerup.MULTI_BALL:
                        game.balls = [j for b in game.balls for j in b.generate_multiballs()]
                    elif self.type == Powerup.FAST_BALLS:
                        game.change_all_ball_speeds(3)
                    elif self.type == Powerup.SLOW_BALLS:
                        game.change_all_ball_speeds(-3)
                    elif self.type == Powerup.PORTAL:
                        game.activate_portal()
                    elif self.type == Powerup.EXTRA_LIFE:
                        game.lives += 1

        self.image = f"barrel{int(self.type)}{self.time // 10 % 10}"

        self.shadow.pos = (self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET)

class Impact(Actor):
    def __init__(self, pos, type_):
        super().__init__("blank", pos)
        self.type = type_
        self.time = 0

    def update(self):
        self.image = "impact" + hex(self.type)[2:] + str(self.time // 4)
        self.time += 1

class Ball(Actor):
    def __init__(self, x=0, y=0, dir=Vector2(0,0), stuck_to_bat=True, speed=BALL_START_SPEED):
        super().__init__("ball0", (0,0))
        self.x = x
        self.y = y
        self.dir = Vector2(dir)
        self.stuck_to_bat = stuck_to_bat
        self.bat_offset = BALL_INITIAL_OFFSET
        self.speed = speed
        self.speed_up_timer = 0
        self.time_since_touched_bat = 0
        self.time_since_damaged_brick = 0
        self.shadow = Actor("balls", (self.x + 16, self.y + 16))

    def update(self):
        self.time_since_damaged_brick += 1

        if self.stuck_to_bat:
            self.x = game.bat.x + self.bat_offset
            self.y = game.bat.y - BALL_RADIUS

            if game.controls.fire_pressed():
                self.stuck_to_bat = False
                _, self.dir = self.get_bat_bounce_vector()
        else:
            self.time_since_touched_bat += 1

            self.speed_up_timer += 1
            if self.time_since_touched_bat > 5 * 60:
                self.speed_up_timer += 1
            interval = BALL_SPEED_UP_INTERVAL \
                    if self.speed < BALL_FAST_SPEED_THRESHOLD else BALL_SPEED_UP_INTERVAL_FAST
            interval2 = interval * 0.75
            if self.speed_up_timer > interval or (self.speed_up_timer > interval2
                                                  and self.time_since_touched_bat > interval2):
                self.increment_speed()
                self.speed_up_timer = 0

            for i in range(self.speed):
                self.x += self.dir.x

                c = game.collide(self.x, self.y, self.dir)
                if c is not None:
                    self.dir.x = -self.dir.x
                    self.x += self.dir.x

                    if c[1]:
                        game.impacts.append(Impact(c[0], 0xc))

                    if c[2] == CollisionType.BRICK:
                        self.time_since_damaged_brick = 0

                    Ball.collision_sound(c[2])

                oy = self.y
                self.y += self.dir.y

                c = game.collide(self.x, self.y, self.dir)
                if c is not None:
                    self.dir.y = -self.dir.y
                    self.y += self.dir.y

                    if c[1]:
                        game.impacts.append(Impact(c[0], 0xc))

                    if c[2] == CollisionType.BRICK:
                        self.time_since_damaged_brick = 0

                    Ball.collision_sound(c[2])

                elif self.dir.y > 0:
                    if oy + BALL_RADIUS <= BAT_TOP_EDGE \
                            and self.y + BALL_RADIUS > BAT_TOP_EDGE:
                                collided_x, new_dir = self.get_bat_bounce_vector()
                                if collided_x:
                                    if game.bat.current_type == BatType.MAGNET:
                                        self.stuck_to_bat = True
                                        self.bat_offset = self.x - game.bat.x
                                        self.dir = Vector2(0,0)
                                    else:
                                        self.dir = new_dir

                                    self.time_since_touched_bat = 0
                                    game.impacts.append(Impact((self.x, self.y), 0xc))
                                    Ball.collision_sound(CollisionType.BAT)

                                    if self.stuck_to_bat:
                                        break

                    elif self.y + BALL_RADIUS > BAT_TOP_EDGE \
                         and self.y < BAT_TOP_EDGE + 15:
                            collided_x, _ = self.get_bat_bounce_vector()
                            if collided_x:
                                dx = 1 if self.x > game.bat.x else -1
                                self.dir = Vector2(dx, uniform(-0.3, -0.1)).normalize()
                                self.time_since_touched_bat = 0
                                game.impacts.append(Impact((self.x, BAT_TOP_EDGE), 0xc))
                                self.speed = min(self.speed + 4, BALL_MAX_SPEED)
                                Ball.collision_sound(CollisionType.BAT_EDGE)

        self.shadow.pos = (self.x + 16, self.y + 16)

    def increment_speed(self):
        self.speed = min(self.speed + 1, BALL_MAX_SPEED)

    def get_bat_bounce_vector(self):
        dx = self.x - game.bat.x
        w = (game.bat.width // 2) + BALL_RADIUS
        if abs(dx) < w:
            vec = Vector2(dx / w, -0.5).normalize()
            return True, vec
        else:
            return False, Vector2(0, -1)

    def generate_multiballs(self):
        balls = []
        for i in range(3):
            vec = self.dir.rotate(i * 120)
            if abs(vec.y) < 0.15:
                vec = Vector2(uniform(-1,1), -1).normalize()
            balls.append(Ball(self.x, self.y, vec, False, self.speed))
        return balls

    @staticmethod
    def collision_sound(collision_type):
        if collision_type == CollisionType.BRICK or collision_type == CollisionType.INDESTRUCTIBLE_BRICK:
            game.play_sound("hit_brick")
        elif collision_type == CollisionType.WALL:
            game.play_sound("hit_wall")
        elif collision_type == CollisionType.BAT:
            if game.bat.current_type == BatType.MAGNET:
                game.play_sound("ball_stick")
            else:
                game.play_sound("hit_fast")
        elif collision_type == CollisionType.BAT_EDGE:
            if game.bat.current_type == BatType.MAGNET:
                game.play_sound("ball_stick")
            else:
                game.play_sound("hit_veryfast")

class Bat(Actor):
    def __init__(self, controls):
        super().__init__("blank", (320, 590), anchor=("center",15))
        self.controls = controls
        self.fire_timer = 0
        self.current_type = BatType.NORMAL
        self.target_type = BatType.NORMAL
        self.frame = 0
        self.shadow = Actor("blank", (self.x + 16, self.y + 16), anchor=("center", 15))

    def update(self):
        if self.target_type != BatType.NORMAL \
                and self.target_type == self.current_type and self.frame < 12:
                    self.frame += 1
        
        if self.target_type != self.current_type and self.frame > 0:
            self.frame -= 1

        if self.frame == 0:
            self.current_type = self.target_type

        self.image = f"bat{int(self.current_type)}{self.frame // 4}"

        self.fire_timer -= 1
        if self.controls.fire_down() and self.current_type == BatType.GUN \
                and self.frame == 12 and self.fire_timer <= 0:
                    self.fire_timer = FIRE_INTERVAL
                    self.image += "f"
                    game.bullets.append(Bullet((self.x - 20, self.y), 0))
                    game.bullets.append(Bullet((self.x + 20, self.y), 1))
                    game.play_sound("laser")

        new_x = self.x + self.controls.get_x()

        min_x = BAT_MIN_X + (self.width // 2)
        new_x = max(min_x, new_x)

        if not game.portal_active:
            max_x = BAT_MAX_X - (self.width // 2)
            new_x = min(max_x, new_x)

        self.x = new_x

        if game.portal_active and new_x == BAT_MAX_X - (self.width // 2):
            self.portal_animation_active = True

        self.shadow.x = self.x + 16
        self.shadow.y = self.y + 16
        self.shadow.image = f"bats{str(int(self.current_type))}{self.frame // 4}"

    def change_type(self, type):
        self.target_type = type

    def is_portal_transition_complete(self):
        return self.x - (self.width // 2) >= WIDTH

def brick_collide(x, y, grid_x, grid_y, r):
    x0, y0 = x - r, y - r
    x1, y1 = x + r, y + r

    xb0 = grid_x * BRICK_WIDTH + BRICKS_X_START
    yb0 = grid_y * BRICK_HEIGHT + BRICKS_Y_START
    xb1 = xb0 + BRICK_WIDTH
    yb1 = yb0 + BRICK_HEIGHT
    
    xbc = (xb0+xb1) // 2
    ybc = (yb0+yb1) // 2

    if x1 > xb0 and x0 < xb1 and y > yb0 and y < yb1:
        if x < xbc:
            return xb0, y
        else:
            return xb1, y

    if x > xb0 and x < xb1 and y1 > yb0 and y0 < yb1:
        if y < ybc:
            return x, yb0
        else:
            return x, yb1

    pos_vector = Vector2(x, y)

    closest = min([(xb0,yb0), (xb1,yb0), (xb0,yb1), (xb1,yb1)],
                  key=lambda p: (pos_vector - Vector2(p)).length_squared())

    if (pos_vector - Vector2(closest)).length() < r:
        return closest
    else:
        return None

class Game:
    def __init__(self, controls=None, lives=3):
        self.controls = controls if controls else AIControls()
        self.lives = lives
        self.score = 0
        self.new_level(0)

    def new_level(self, level_num):
        self.play_sound("start_game")

        if level_num >= len(LEVELS):
            level_num = 0

        self.brick_surface = surface.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
        self.brick_surface.fill((0, 0, 0, 0))

        self.shadow_surface = surface.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
        self.shadow_surface.fill((0, 0, 0, 0))

        level = get_mirrored_level(LEVELS[level_num])

        self.num_rows, self.num_cols = len(level), len(level[0])

        self.bricks = [[None if level[y][x] == " "
                        else int(level[y][x], 16) for x in range(self.num_cols)]
                       for y in range(self.num_rows)]

        self.bricks_remaining = 0
        for y in range(self.num_rows):
            for x in range(self.num_cols):
                self.redraw_brick(x, y)
                if self.bricks[y][x] != None and self.bricks[y][x] != 13:
                    self.bricks_remaining += 1

        self.balls = [Ball()]
        self.bat = Bat(self.controls)

        self.bullets, self.barrels, self.impacts = [], [], []

        self.level_num = level_num
        self.portal_active = False
        self.portal_frame = 0
        self.portal_timer = 0

    def redraw_brick(self, x, y):
        screen_x = x * BRICK_WIDTH + BRICKS_X_START
        screen_y = y * BRICK_HEIGHT + BRICKS_Y_START

        if self.bricks[y][x] != None:
            brick_image = getattr(images, "brick" + hex(self.bricks[y][x])[2:])
            self.brick_surface.blit(brick_image, (screen_x, screen_y))
            self.shadow_surface.blit(images.bricks, (screen_x + SHADOW_OFFSET,
                                                     screen_y + SHADOW_OFFSET))
        else:
            self.brick_surface.fill((0,0,0,0), (screen_x, screen_y, BRICK_WIDTH, BRICK_HEIGHT))
            self.shadow_surface.fill((0,0,0,0), (screen_x + SHADOW_OFFSET, screen_y + SHADOW_OFFSET,
                                                 BRICK_WIDTH, BRICK_HEIGHT))

    def collide(self, x, y, dir_, r=BALL_RADIUS):
        dx,dy = dir_
        if dx < 0 and x < LEFT_EDGE + r:
            return (LEFT_EDGE, y), True, CollisionType.WALL
        if dx > 0 and x > RIGHT_EDGE - r:
            return (RIGHT_EDGE, y), True, CollisionType.WALL
        if dy < 0 and y < TOP_EDGE + r:
            return (x, TOP_EDGE), True, CollisionType.WALL

        x0 = max(0, math.floor((x-BRICKS_X_START-r)/BRICK_WIDTH))
        y0 = max(0, math.floor((y-BRICKS_Y_START-r)/BRICK_HEIGHT))
        x1 = min(self.num_cols - 1, math.floor((x-BRICKS_X_START+r) / BRICK_WIDTH))
        y1 = min(self.num_rows - 1, math.floor((y-BRICKS_Y_START+r) / BRICK_HEIGHT))

        for yb in range(y0, y1+1):
            for xb in range(x0, x1+1):
                if self.bricks[yb][xb] != None:
                    c = brick_collide(x, y, xb, yb, r)
                    if c is not None:
                        center_pos = (xb * BRICK_WIDTH + BRICKS_X_START + BRICK_WIDTH // 2,
                                      yb * BRICK_HEIGHT + BRICKS_Y_START + BRICK_HEIGHT // 2)
                        collision_type = CollisionType.BRICK

                        if self.bricks[yb][xb] >= 12:
                            if self.bricks[yb][xb] == 13:
                                collision_type = CollisionType.INDESTRUCTIBLE_BRICK
                            self.impacts.append(Impact(center_pos, 13))
                            if self.bricks[yb][xb] == 12:
                                self.bricks[yb][xb] = 11
                        else:
                            self.impacts.append(Impact(center_pos, self.bricks[yb][xb]))

                            if random() < POWERUP_CHANCE:
                                self.barrels.append(Barrel(center_pos))

                            self.bricks[yb][xb] = None
                            self.redraw_brick(xb, yb)

                            self.bricks_remaining -= 1
                            if self.bricks_remaining == 0:
                                self.activate_portal()

                            self.score += 10

                        return c, False, collision_type

        return None

    def activate_portal(self):
        self.portal_active = True
        self.play_sound("portal_exit")

    def update(self):
        for obj in [self.bat] + self.balls:
            obj.update()

        self.balls = [obj for obj in self.balls if obj.y < HEIGHT]

        if len(self.balls) == 0:
            if self.lives > 0 or self.in_demo_mode():
                self.lives -= 1
                self.balls = [Ball()]
                self.bat.change_type(BatType.NORMAL)

            self.play_sound("lose_life")

        for obj in self.impacts + self.barrels + self.bullets:
            obj.update()

        self.impacts = [obj for obj in self.impacts if obj.time < 16]
        self.barrels = [obj for obj in self.barrels if obj.y < HEIGHT]
        self.bullets = [obj for obj in self.bullets if obj.alive]

        if self.portal_active:
            if self.portal_frame < 3:
                self.portal_timer -= 1
                if self.portal_timer <= 0:
                    self.portal_timer = PORTAL_ANIMATION_SPEED
                    self.portal_frame += 1
            elif self.bat.is_portal_transition_complete():
                self.new_level(self.level_num + 1)

        if self.detect_stuck_balls():
            changed_any = False
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    if self.bricks[row][col] == 13:
                        self.bricks[row][col] = 12
                        self.redraw_brick(col, row)
                        changed_any = True

            if changed_any:
                self.play_sound("bat_small", 1)

            if len(self.balls) > 0:
                self.balls[0].time_since_touched_bat = 0

    def detect_stuck_balls(self):
        if len(self.balls) == 0:
            return False
        for ball in self.balls:
            if ball.time_since_damaged_brick < 30 * 60 \
                    or ball.time_since_touched_bat < 30 * 60:
                        return False
        return True

    def draw(self):
        screen.blit(f"arena{self.level_num % len(LEVELS)}", (0,0))
        screen.blit(f"portal_exit{self.portal_frame}", (WIDTH - 70 - 20, HEIGHT - 70))
        screen.blit(f"portal_meanie00", (110,40))
        screen.blit(f"portal_meanie10", (440,40))

        screen.surface.set_clip((20, 42, 600, 598))

        screen.blit(self.shadow_surface, (0, 0))

        for obj in self.barrels + self.balls + [self.bat]:
            obj.shadow.draw()

        screen.blit(self.brick_surface, (0, 0))

        for obj in self.balls + [self.bat] + self.barrels + self.bullets:
            obj.draw()

        screen.surface.set_clip(None)

        for obj in self.impacts:
            obj.draw()

        if not self.in_demo_mode():
            self.draw_score()
            self.draw_lives()

    def draw_score(self):
        x = 15
        for digit in str(self.score):
            image = "digit" + digit
            screen.blit(image, (x, 50))
            x += 55

    def draw_lives(self):
        x = 0
        for i in range(self.lives):
            screen.blit("life", (x, HEIGHT-20))
            x += 50

    def play_sound(self, name, count=1):
        if not self.in_demo_mode():
            try:
                getattr(sounds, name + str(randint(0, count - 1))).play()
            except Exception as e:
                print(e)

    def change_all_ball_speeds(self, change):
        for b in self.balls:
            b.speed = min(max(b.speed + change, BALL_MIN_SPEED), BALL_MAX_SPEED)

    def in_demo_mode(self):
        return isinstance(self.controls, AIControls)

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
    TITLE = 1,
    PLAY = 2,
    GAME_OVER = 3

def update():
    global state, game, total_frames
    total_frames += 1

    update_controls()

    if state == State.TITLE:
        ai_controls.update()
        game.update()

        for controls in (keyboard_controls, joystick_controls):
            if controls is not None and controls.fire_pressed():
                game = Game(controls)
                state = State.PLAY
                stop_music()
                break

    elif state == State.PLAY:
        if game.lives > 0:
            game.update()
        else:
            game.play_sound("game_over")
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        for controls in (keyboard_controls, joystick_controls):
            if controls is not None and controls.fire_pressed():
                game = Game(ai_controls)
                state = State.TITLE
                play_music("title_theme")

def draw():
    game.draw()
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit("startgame", (20,80))
        screen.blit(f"start{(total_frames // 4) % 13}", (WIDTH//2 - 250//2, 530))
    elif state == State.GAME_OVER:
        screen.blit(f"gameover{(total_frames // 4) % 15}", (WIDTH//2 - 450//2, 450))

def play_music(name):
    try:
        music.play(name)
    except Exception:
        pass

def stop_music():
    try:
        music.stop()
    except Exception:
        pass

try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)
    play_music("title_theme")
    music.set_volume(0.3)
except Exception:
    pass

keyboard_controls = KeyboardControls()
ai_controls = AIControls()
setup_joystick_controls()

state = State.TITLE
game = Game(ai_controls)
total_frames = 0

run()
