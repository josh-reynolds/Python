from enum import Enum, IntEnum
import pygame
from pygame import surface, Vector2
from engine import *

WIDTH = 800                  ###
HEIGHT = 480                 ###
TITLE = 'Brikz'

PORTAL_ANIMATION_SPEED = 5       ###
BRICK_WIDTH = 20           ###
BRICK_HEIGHT = 20           ###
BRICKS_X_START = 20           ###
BRICKS_Y_START = 20           ###
SHADOW_OFFSET = 10           ###

BAT_MIN_X = 5         ###
BAT_MAX_X = 15         ###

BALL_START_SPEED = 5       ###
BALL_INITIAL_OFFSET = 5       ###
BALL_RADIUS = 5       ###

LEVELS = [0,0,0]       ###

def get_mirrored_level(a):          ###
    return [['0','0'],['0','0'],['0','0']]              ###

class KeyboardControls:      ###
    def update(self):     ###
        pass              ###
    def fire_pressed(self):
        pass                  ###

class AIControls:         ###
    def update(self):     ###
        pass              ###
    def fire_down(self):    ###
        pass              ###
    def get_x(self):    ###
        return 1         ###
    def fire_pressed(self):
        pass                  ###

class BatType(IntEnum):
    NORMAL, MAGNET, GUN, EXTENDED, SMALL = 0, 1, 2, 3, 4

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
        self.time_since_touchd_bat = 0
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

        self.balls =[Ball()]
        self.bat = Bat(self.controls)

        self.barrels, self.bullets, self.impacts = [], [], []

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
        x = 0
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

keyboard_controls = KeyboardControls()
ai_controls = AIControls()
setup_joystick_controls()

state = State.TITLE
game = Game(ai_controls)
total_frames = 0

run()
