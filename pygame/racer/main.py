import math
import platform
import sys
import time
from enum import Enum
from abc import ABC, abstractmethod
from random import choice, uniform, randint
import pygame
from pygame.math import Vector2, Vector3
from engine import *

USE_GFXDRAW = False

if USE_GFXDRAW:
    import pygame.gfxdraw

# version checks not present in book sources
if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

engine = sys.modules["engine"]
engine_version = [int(s) if s.isnumeric() else s
                  for s in engine.__version__.split('.')]

if engine_version < [1,4]:
    print(f"This game requires at least version 1.4 of the engine. "
          f"You are using version {engine.__version__}. Please upgrade.")
    sys.exit()

WIDTH = 960
HEIGHT = 540
TITLE = "Racer"

PERFORMANCE_MODE = False

if not PERFORMANCE_MODE:
    SHOW_SCENERY = True
    SHOW_TRACKSIDE = True
    SHOW_RUMBLE_STRIPS = True
    SHOW_YELLOW_LINES = True
    OUTLINE_W = 0
    VIEW_DISTANCE = 200
else:
    SHOW_SCENERY = False
    SHOW_TRACKSIDE = False
    SHOW_RUMBLE_STRIPS = False
    SHOW_YELLOW_LINES = False
    OUTLINE_W = 1
    VIEW_DISTANCE = 150

CLIPPING_PLANE = -0.25
CLIPPING_PLANE_CARS = -0.08
SCALE_FUNC = pygame.transform.scale
MAX_SCENERY_SCALED_WIDTH = WIDTH * 2
MAX_CAR_SCALED_WIDTH = WIDTH * 1

SPACING = 1

TRACK_W = 3000
HALF_STRIPE_W = 25
HALF_RUMBLE_STRIP_W = 250
HALF_YELLOW_LINE_W = 80
YELLOW_LINE_EDGE_DISTANCE = 150

TRACK_COLOR = (35, 96, 198)
STRIPE_COLOR = (70, 192, 198)
TRACKSIDE_COLOR_1 = (0, 77, 180)
TRACKSIDE_COLOR_2 = (50, 77, 170)
YELLOW_LINE_COL = (0, 161, 88)
RUMBLE_COL_1 = (0, 116, 255)
RUMBLE_COL_2 = (0, 58, 135)

SECTION_VERY_SHORT = 25
SECTION_SHORT = 50
SECTION_MEDIUM = 100
SECTION_LONG = 200

LAMP_X = TRACK_W//2 + 300
BILLBOARD_X = TRACK_W//2 + 600

LOSE_GRIP_SPEED = 50
ZERO_GRIP_SPEED = 100

PLAYER_ACCELERATION_MAX = 20
PLAYER_ACCELERATION_MIN = 10
HIGH_ACCEL_THRESHOLD = 30

CORNER_OFFSET_MULTIPLIER = 5.8
STEERING_STRENGTH = 72

CPU_CAR_MIN_TARGET_SPEED = 40
CPU_CAR_MAX_TARGET_SPEED = 65

NUM_LAPS = 5
NUM_CARS = 20
GRID_CAR_SPACING = 0.55

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

SKID_SOUND_START_GRIP = 0.8

CAMERA_FOLLOW_DISTANCE = 2

FIXED_TIMESTEP = 1/60

SPECIAL_FONT_SYMBOLS = {'xb_a':'%'}
SPECIAL_FONT_SYMBOLS_INVERSE = dict((v,k) for k,v in SPECIAL_FONT_SYMBOLS.items())

fade_to_black_image = pygame.Surface((WIDTH,HEIGHT))

SHOW_TRACK_PIECE_INDEX = False
SHOW_TRACK_PIECE_OFFSETS = False
SHOW_CPU_CAR_SPEEDS = False
SHOW_DEBUG_TEXT = False
SHOW_PROFILE_TIMINGS = False

class Profiler:
    def __init__(self, name=""):
        self.start_time = time.perf_counter()
        self.name = name

    def get_ms(self):
        end_time = time.perf_counter()
        diff = end_time - self.start_time
        return diff * 1000

    def __str__(self):
        return f"{self.name}: {self.get_ms()}ms"

def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min) * (old_val - old_min) / (old_max - old_min) + new_min

def remap_clamp(old_val, old_min, old_max, new_min, new_max):
    lower_limit = min(new_min, new_max)
    upper_limit = max(new_min, new_max)
    return min(upper_limit, max(lower_limit, remap(old_val, old_min, old_max, new_min, new_max)))

def inverse_lerp(a, b, value):
    if a != b:
        return min(1, max(0, ((value - a) / (b - a))))
    else:
        return 0

def sign(x):
    if x == 0:
        return 0
    else:
        return -1 if x < 0 else 1

def move_towards(n, target, speed):
    if n < target:
        return min(n + speed, target)
    else:
        return max(n - speed, target)

def format_time(seconds):
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"

def get_char_image_and_width(char, font):
    if char == " ":
        return None, 30
    else:
        if char in SPECIAL_FONT_SYMBOLS_INVERSE:
            image = getattr(images, SPECIAL_FONT_SYMBOLS_INVERSE[char])
        else:
            image = getattr(images, font + "0" + str(ord(char)))
        return image, image.get_width()

TEXT_GAP_X = {"font":-6, "status1b_":0, "status2_":0}

def text_width(text, font):
    return sum([get_char_image_and_width(c,font)[1] for c in text]) + TEXT_GAP_X[font] * (len(text)-1)

def draw_text(text, x, y, center=False, font="font"):
    if center:
        x -= text_width(text, font) // 2
    for char in text:
        image, width = get_char_image_and_width(char, font)
        if image is not None:
            screen.blit(image, (x,y))
        x += width + TEXT_GAP_X[font]

class Controls(ABC):
    NUM_BUTTONS = 2

    def __init__(self):
        self.button_previously_down = [False for i in range(Controls.NUM_BUTTONS)]
        self.is_button_pressed = [False for i in range(Controls.NUM_BUTTONS)]

    def update(self):
        for button in range(Controls.NUM_BUTTONS):
            button_down = self.button_down(button)
            self.is_button_pressed[button] = button_down and not self.button_previously_down[button]
            self.button_previously_down[button] = button_down

    @abstractmethod
    def get_x(self):
        pass

    @abstractmethod
    def button_down(self, button):
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

    def button_down(self, button):
        if button == 0:
            return keyboard.lctrl or keyboard.z
        elif button == 1:
            return keyboard.lshift or keyboard.x

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
            return axis_value

    def get_x(self):
        return self.get_axis(0)

    def get_y(self):
        return self.get_axis(1)

    def button_down(self, button):
        if self.joystick.get_numbuttons() <= button:
            print("Warning: main controller does not have enough buttons!")
            return False
        return self.joystick.get_button(button) != 0

class Scenery:
    def __init__(self, x, image, min_draw_distance=0, max_draw_distance=VIEW_DISTANCE // 2,
                 scale=1, collision_zones=()):
        self.x = x
        self.image = image
        self.min_draw_distance = min_draw_distance
        self.max_draw_distance = max_draw_distance
        self.scale = scale
        self.collision_zones = collision_zones

    def get_image(self):
        return self.image

class StartGantry(Scenery):
    def __init__(self):
        super().__init__(0, images.start0, min_draw_distance=1, max_draw_distance=VIEW_DISTANCE,
                         scale=4, collision_zones=((-3000,-2400),(2400,3000)))

    def get_image(self):
        if game.start_timer > 0:
            index = int(remap(game.start_timer, 4, 0, 0, 4))
        else:
            index = 4 if int(game.timer * 2) % 2 == 0 else 5
        image = "start" + str(index)
        self.image = getattr(images, image)
        return self.image

class Billboard(Scenery):
    def __init__(self, x, image):
        half_width = image.get_width() / 2
        scale = 2
        super().__init__(x, image, scale=scale, collision_zones=((-half_width*scale,half_width*scale),))

class LampLeft(Scenery):
    def __init__(self):
        super().__init__(LAMP_X, images.left_light, scale=2, collision_zones=((350,1200),))

class LampRight(Scenery):
    def __init__(self):
        super().__init__(-LAMP_X, images.right_light, scale=2, collision_zones=((-1200,-350),))

class TrackPiece:
    def __init__(self, scenery=(), offset_x=0, offset_y=0, 
                 cpu_max_target_speed=None, col=TRACK_COLOR,
                 width=TRACK_W):
        self.scenery = scenery
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.cpu_max_target_speed = cpu_max_target_speed
        self.col = col
        self.width = width
        self.cars = []

class TrackPieceStartLine(TrackPiece):
    def __init__(self):
        super().__init__(scenery=[StartGantry()], col=(255,255,255))

class Car:
    def __init__(self, pos, car_letter):
        self.pos = pos
        self.image = f"car_{car_letter}_0_0"
        self.speed = 0
        self.grip = 1
        self.car_letter = car_letter
        self.track_piece = None
        self.tire_rotation = 0

    def update(self, delta_time):
        self.pos.z -= self.speed * delta_time
        self.update_current_track_piece()
        self.tire_rotation += delta_time * self.speed * 0.75

    def update_current_track_piece(self):
        current_track_piece = self.track_piece
        idx = game.get_track_piece_for_z(self.pos.z)
        if idx is not None:
            self.track_piece = game.track[idx]
            if self.track_piece is not current_track_piece:
                if current_track_piece is not None:
                    current_track_piece.cars.remove(self)
                self.track_piece.cars.append(self)

    def update_sprite(self, angle, braking, boost=False):
        if self.speed == 0:
            frame = 0
        elif braking:
            frame = 3
        elif boost:
            frame = int(self.tire_rotation % 2) + 4
        else:
            frame = int(self.tire_rotation % 2) + 1
        self.image = f"car_{self.car_letter}_{angle}_{frame}"

class CPUCar(Car):
    def __init__(self, pos, accel, speed):
        super().__init__(pos, choice(('b','c','d','e')))
        self.accel = PLAYER_ACCELERATION_MAX * accel
        self.target_speed = speed
        self.target_x = pos.x
        self.steering = 0
        self.change_speed_timer = uniform(2,4)

    def update(self, delta_time):
        if game.race_complete:
            self.target_speed = game.player_car.speed

        self.speed = move_towards(self.speed, self.target_speed, self.accel * delta_time)
        self.pos.x = move_towards(self.pos.x, self.target_x, 400 * delta_time)

        super().update(delta_time)

        track_piece_idx, _ = game.get_first_track_piece_ahead(self.pos.z)
        if track_piece_idx is not None:
            self.steering = game.track[track_piece_idx].offset_x

        self.change_speed_timer -= delta_time
        if self.change_speed_timer <= 0 and not game.race_complete:
            self.target_speed += uniform(-4, 6)
            self.target_speed = min(max(self.target_speed, CPU_CAR_MIN_TARGET_SPEED), CPU_CAR_MAX_TARGET_SPEED)

            if track_piece_idx is not None:
                target_speed_override = game.track[track_piece_idx].cpu_max_target_speed
                if target_speed_override is not None and self.target_speed > target_speed_override:
                    self.target_speed = uniform(target_speed_override-3, target_speed_override)

            def is_target_x_too_close_to_nearby_cars():
                for car in game.cars:
                    if car is not self and abs(self.pos.z - car.pos.z) < 20 \
                            and abs(self.target_x - car.pos.x) < 300:
                                return True
                return False

            for attempt in range(0,20):
                self.target_x = uniform(-1000,1000)
                if not is_target_x_too_close_to_nearby_cars():
                    break

            self.change_speed_timer = uniform(2,4)

class PlayerCar(Car):
    def __init__(self, pos, controls):
        super().__init__(pos, 'a')
        self.pos = pos
        self.controls = controls
        self.offset_x_change = 0
        self.resetting = False
        self.explode_timer = None
        self.last_checkpoint_idx = None
        self.lap = 1
        self.lap_time = 0
        self.race_time = 0
        self.fastest_lap = None
        self.last_lap_was_fastest = False
        self.braking = False

        try:
            self.engine_sounds = [getattr(sounds, "engine_short" + str(i))
                                  for i in range(40)]
            self.skid_sound = sounds.skid_loop0
        except Exception:
            self.engine_sounds = []
            self.skid_sound = None

        self.current_engine_sound = None
        self.current_engine_sound_idx = -1
        self.update_engine_sound()

        self.skid_sound_playing = False
        self.grass_sound_repeat_timer = 0
        self.on_grass = False

        self.prev_position = NUM_CARS - 1

    def stop_engine_sound(self):
        if self.current_engine_sound is not None:
            try:
                self.current_engine_sound.stop()
            except Exception:
                pass

    def update(self, delta_time):
        if not game.race_complete:
            self.lap_time += delta_time
            self.race_time += delta_time

        self.grass_sound_repeat_timer -= delta_time
        self.update_engine_sound()

        current_position = game.cars.index(self)

        if current_position != self.prev_position:
            if abs(self.speed - game.cars[self.prev_position].speed) > 4:
                game.play_sound("overtake", 6)
            self.prev_position = current_position

        if self.resetting:
            if self.explode_timer is not None:
                self.explode_timer += 1
                if self.explode_timer > 31:
                    self.explode_timer = None
            else:
                self.pos.x = move_towards(self.pos.x, 0, 2000 + delta_time)
                self.resetting = self.pos.x != 0

        x_move = accel = 0

        if not self.resetting:
            self.braking = False

            if not game.race_complete:
                self.controls.update()
                if self.controls.button_down(0):
                    accel = PLAYER_ACCELERATION_MAX if self.speed < HIGH_ACCEL_THRESHOLD \
                            else PLAYER_ACCELERATION_MIN
                    self.speed += accel * delta_time
                elif self.controls.button_down(1):
                    self.braking = True
                    self.speed = max(0, self.speed - delta_time * 10)

            drag_factor = 0.9975
            if self.on_grass:
                drag_factor -= 0.0025

            self.speed *= drag_factor ** (delta_time / (1/60))

            if self.offset_x_change != 0:
                if self.speed > LOSE_GRIP_SPEED and sign(self.get_x_input() == -sign(self.offset_x_change)):
                    self.grip = remap_clamp(self.speed, LOSE_GRIP_SPEED, ZERO_GRIP_SPEED, 1, 0)
                else:
                    self.grip = 1
                if not game.race_complete:
                    self.pos.x -= self.offset_x_change * CORNER_OFFSET_MULTIPLIER
            else:
                self.grip = 1

            previous_track_piece_idx, _ = game.get_first_track_piece_ahead(self.pos.z)

            if self.speed > 0 and not game.race_complete:
                x_move = self.get_x_input() * self.speed * STEERING_STRENGTH * self.grip * delta_time
                self.pos.x -= x_move

            super().update(delta_time)
            
            for car in game.cars:
                if car is not self:
                    vec = self.pos - car.pos
                    COLLIDE_FRONT_DISTANCE_Z = 0.6
                    COLLIDE_BACK_DISTANCE_Z = 1.2
                    if abs(vec.x) < 260 and vec.z < COLLIDE_FRONT_DISTANCE_Z \
                            and vec.z > -COLLIDE_BACK_DISTANCE_Z:
                                midpoint = (self.pos.z - car.pos.z) / 2 + car.pos.z
                                if abs(vec.z) < 0.2:
                                    self.pos.x += sign(vec.x) * 50
                                    car.pos.x -= sign(vec.x) * 50
                                elif vec.z > 0:
                                    self.speed = max(car.speed - 3, 0)
                                    car.speed = max(car.speed, self.speed + 3)
                                    car.target_speed = car.speed
                                    self.pos.z = midpoint + COLLIDE_FRONT_DISTANCE_Z * 0.6
                                    car.pos.z = midpoint - COLLIDE_FRONT_DISTANCE_Z * 0.6
                                    game.play_sound("bump", 6)
                                else:
                                    self.speed = max(self.speed, car.speed + 3)
                                    car.speed = max(self.speed - 3, 0)
                                    self.pos.z = midpoint - COLLIDE_BACK_DISTANCE_Z * 0.6
                                    car.pos.z = midpoint + COLLIDE_BACK_DISTANCE_Z * 0.6
                                    game.play_sound("bump_behind")

            track_piece_idx, _ = game.get_first_track_piece_ahead(self.pos.z)
            if track_piece_idx is not None:
                track_piece = game.track[track_piece_idx]

                for scenery in track_piece.scenery:
                    for collision_zone in scenery.collision_zones:
                        zone_left = scenery.x + collision_zone[0]
                        zone_right = scenery.x + collision_zone[1]
                        if zone_left < self.pos.x < zone_right:
                            self.speed = 0
                            self.resetting = True
                            self.explode_timer = 0
                            game.play_sound("explosion")

                for i in range(previous_track_piece_idx, track_piece_idx+1):
                    if isinstance(game.track[i], TrackPieceStartLine):
                        if self.last_checkpoint_idx is not None and self.last_checkpoint_idx != i:
                            self.lap += 1

                            if self.fastest_lap is None or self.lap_time < self.fastest_lap:
                                self.fastest_lap = self.lap_time
                                self.last_lap_was_fastest = True
                                game.play_sound("fastlap")
                            else:
                                self.last_lap_was_fastest = False

                            if self.lap == NUM_LAPS:
                                game.play_sound("final_lap")

                            self.lap_time = 0

                        self.last_checkpoint_idx = i

                if abs(self.pos.x) + 100 > track_piece.width / 2:
                    self.on_grass = True
                    if self.grass_sound_repeat_timer <= 0:
                        game.play_sound("hit_grass")
                        self.grass_sound_repeat_timer = 0.15

                    if abs(self.pos.x) > 6000:
                        self.speed = 0
                        self.resetting = True
                else:
                    self.on_grass = False

        if self.skid_sound is not None:
            if self.resetting or self.grip > SKID_SOUND_START_GRIP or self.get_x_input() == 0:
                volume = 0
            else:
                volume = remap_clamp(self.grip, SKID_SOUND_START_GRIP, 0.5, 0, 1)
                if track_piece_idx is not None:
                    track_piece = game.track[track_piece_idx]
                    volume *= remap_clamp(abs(track_piece.offset_x), 0, 15, 0, 1)

            if volume > 0:
                if not self.skid_sound_playing:
                    self.skid_sound.play(loops=-1, fade_ms=100)
                    self.skid_sound_playing = True
                self.skid_sound.set_volume(volume)
            else:
                self.skid_sound_playing = False
                self.skid_sound.fadeout(250)

        if self.explode_timer is not None:
            self.image = f"explode{self.explode_timer//2:02}"
        else:
            direction = 0
            if x_move < 0:
                direction = -1
            elif x_move > 0:
                direction = 1
            boost = accel > 0 and self.speed < HIGH_ACCEL_THRESHOLD and self.speed > 0
            self.update_sprite(direction, self.braking, boost)
        
    def update_engine_sound(self):
        sound_index = min(int(self.speed * 0.6), len(self.engine_sounds) - 1)
        if sound_index != self.current_engine_sound_idx:
            self.current_engine_sound_idx = sound_index
            old_sound = self.current_engine_sound
            self.current_engine_sound = self.engine_sounds[sound_index]
            self.current_engine_sound.set_volume(0.3)
            try:
                if old_sound is not None:
                    old_sound.fadeout(150)
                self.current_engine_sound.play(loops=-1, fade_ms=100)
            except:
                pass

    def get_x_input(self):
        return self.controls.get_x()

    def set_offset_x_change(self, value):
        self.offset_x_change = value

def generate_scenery(track_i, image=images.billboard00, interval=40, lamps=True):
    if track_i % interval == 0:
        return[Billboard(BILLBOARD_X, image), Billboard(-BILLBOARD_X, image)]
    elif lamps and track_i % 30 == 0:
        return[LampLeft(), LampRight()]
    else:
        return []

def make_track():
    track = []
    for lap in range(NUM_LAPS + 1):
        track.extend([TrackPiece(scenery=generate_scenery(i, images.billboard02)) 
                      for i in range(15)])

        track.append(TrackPieceStartLine())

        track.extend([TrackPiece() for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=-4, offset_y=0, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(scenery=generate_scenery(i,images.billboard01)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=0, offset_y=-1, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_VERY_SHORT)])

        track.extend([TrackPiece(offset_x=0, offset_y=-2, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_VERY_SHORT)])

        track.extend([TrackPiece(offset_x=-2, offset_y=-1, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_VERY_SHORT)])

        track.extend([TrackPiece(offset_x=-5, offset_y=0, 
                                 scenery=generate_scenery(i,images.billboard03)) 
                      for i in range(SECTION_VERY_SHORT)])

        track.extend([TrackPiece(offset_x=-10, offset_y=0, 
                                 scenery=generate_scenery(i,images.billboard03)) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(scenery=generate_scenery(i)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=13, offset_y=1, 
                                 scenery=generate_scenery(i, images.arrow_left, interval=10)) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(offset_x=0, offset_y=0, 
                                 scenery=generate_scenery(i,images.billboard02)) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(offset_x=0, offset_y=2, 
                                 scenery=generate_scenery(i,images.billboard02)) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(offset_x=-3, offset_y=-1, 
                                 scenery=generate_scenery(i,images.billboard01)) 
                      for i in range(SECTION_LONG)])

        track.extend([TrackPiece(offset_x=0, offset_y=-4, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(offset_x=0, offset_y=2, 
                                 scenery=generate_scenery(i,images.billboard03)) 
                      for i in range(SECTION_LONG)])

        for j in range(1,10):
            track.extend([TrackPiece(offset_x=j, offset_y=j, 
                                     scenery=generate_scenery(i)) 
                          for i in range(SECTION_VERY_SHORT)])

        for j in range(1,10):
            track.extend([TrackPiece(offset_x=0, offset_y=-j, 
                                     scenery=generate_scenery(i)) 
                          for i in range(SECTION_VERY_SHORT)])

        track.extend([TrackPiece(cpu_max_target_speed=60, 
                                 scenery=[]) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(cpu_max_target_speed=58, 
                                 scenery=generate_scenery(i, images.arrow_right, interval=10, lamps=False)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(cpu_max_target_speed=58, 
                                 scenery=generate_scenery(i, images.arrow_right, interval=10, lamps=False)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=-15, cpu_max_target_speed=55, 
                                 scenery=generate_scenery(i, images.arrow_right, interval=10, lamps=False)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=-13, cpu_max_target_speed=57, 
                                 scenery=generate_scenery(i, images.arrow_right, interval=10, lamps=False)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=-11, offset_y=0, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=-9, offset_y=0, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_SHORT)])

        track.extend([TrackPiece(offset_x=0, offset_y=0, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_MEDIUM)])

        track.extend([TrackPiece(offset_y=math.cos(i/20) * 5, 
                                 scenery=generate_scenery(i)) 
                      for i in range(SECTION_LONG)])

        track.extend([TrackPiece(offset_x=0, offset_y=0.25, 
                                 scenery=generate_scenery(i,images.billboard03)) 
                      for i in range(SECTION_LONG)])

        track.extend([TrackPiece(offset_x=0, offset_y=0, 
                                 scenery=generate_scenery(i,images.billboard03)) 
                      for i in range(SECTION_SHORT)])

    return track

class Game:
    def __init__(self, controls=None):
        self.track = make_track()

        self.player_car = None
        self.camera_follow_car = None
        self.setup_cars(controls)

        self.camera = Vector3(0, 400, 0)

        self.background = images.background
        self.bg_offset = Vector2(-self.background.get_width() // 2, 30)

        self.first_frame = True
        self.on_screen_debug_strs = []
        self.frame_counter = 0
        self.timer = 0
        self.race_complete = False
        self.time_up = False

        if self.player_car is not None:
            self.start_timer = 3.999
            play_music("engines_startline")
        else:
            self.start_timer = 0

    def setup_cars(self, controls):
        self.cars = []
        for i in range(NUM_CARS):
            z = -3 - i * GRID_CAR_SPACING
            x = -400 if i % 2 == 0 else 400
            if i == 0 and controls is not None:
                self.player_car = PlayerCar(Vector3(x, 0, z), controls)
                self.cars.append(self.player_car)
            else:
                target_speed = remap(i, 0, NUM_CARS - 1, CPU_CAR_MIN_TARGET_SPEED, CPU_CAR_MAX_TARGET_SPEED)
                accel = remap(i, 0, NUM_CARS - 1, 1.5, 2)
                self.cars.append(CPUCar(Vector3(x,0,z), speed=target_speed, accel=accel))

        if self.player_car is not None:
            self.camera_follow_car = self.player_car
        else:
            self.camera_follow_car = self.cars[0]

    def update(self, delta_time):
        self.timer += delta_time
        self.frame_counter += 1

        if self.start_timer > 0:
            for car in self.cars:
                car.update_current_track_piece()
            timer_old = self.start_timer
            self.start_timer = max(0, self.start_timer - delta_time)
            if self.start_timer == 0:
                play_music("ambience")
                game.play_sound("gobeep")
            elif int(timer_old) != int(self.start_timer):
                game.play_sound("startbeep")

        old_camera_z = self.camera.z
        prev_ahead, _ = self.get_first_track_piece_ahead(old_camera_z)

        if self.start_timer == 0:
            for car in self.cars:
                car.update(delta_time)

        if not self.race_complete and self.player_car is not None:
            if self.player_car.lap_time >= 60 * 4 or keyboard.escape:
                stop_music()
                self.time_up = True
                self.race_complete = True

            elif self.player_car.lap > NUM_LAPS:
                stop_music()
                self.race_complete = True
                self.play_sound("game_complete")

            self.cars.sort(key = lambda car: car.pos.z)

        self.camera.x = self.camera_follow_car.pos.x
        self.camera.z = self.camera_follow_car.pos.z + CAMERA_FOLLOW_DISTANCE

        new_camera_z = self.camera.z
        new_ahead, _ = self.get_first_track_piece_ahead(new_camera_z)

        dist = old_camera_z - new_camera_z
        offset_change = Vector2(0,0)
        if dist > 0 and not self.first_frame and prev_ahead >= 0 and new_ahead >= 0:
            old_z_next_spacing_boundary = (old_camera_z // SPACING) * SPACING
            new_z_prev_spacing_boundary = ((new_camera_z // SPACING) * SPACING) + SPACING
            prev_track = self.track[prev_ahead]
            new_track = self.track[new_ahead]
            prev_offset = Vector2(prev_track.offset_x, prev_track.offset_y)
            if new_ahead > prev_ahead:
                distance_first = old_camera_z - old_z_next_spacing_boundary
                distance_last = new_z_prev_spacing_boundary - new_camera_z
                fraction_first = distance_first / SPACING
                fraction_last = distance_last / SPACING
                assert(0 <= fraction_first <= 1 and 0 <= fraction_last <= 1)

                new_offset = Vector2(new_track.offset_x, new_track.offset_y)
                offset_change = prev_offset * fraction_first + new_offset * fraction_last

                if new_ahead - prev_ahead > 1:
                    for i in range(prev_ahead + 1, new_ahead):
                        piece = self.track[i]
                        offset_change += Vector2(piece.offset_x, piece.offset_y)
            else:
                fraction = dist / SPACING
                assert(0 <= fraction <= 1)
                offset_change = prev_offset * fraction

            self.bg_offset += offset_change

            while self.bg_offset.x < -self.background.get_width():
                self.bg_offset.x += self.background.get_width()
            while self.bg_offset.x > self.background.get_width():
                self.bg_offset.x -= self.background.get_width()

        if self.player_car is not None:
            self.player_car.set_offset_x_change(offset_change.x)

        if new_ahead < prev_ahead:
            self.bg_offset.x -= self.track[prev_ahead].offset_x
            self.bg_offset.y -= self.track[prev_ahead].offset_y

        self.first_frame = False

    def draw(self):
        if self.bg_offset.y > 0:
            screen.fill( (0,20,117) )
        else:
            screen.fill( (0,77,180) )

        times = {"scenery_scale":0, "car_scale":0, "prepare_draw_cars":0}

        profile_bg = Profiler()
        self.on_screen_debug_strs.append(str(self.bg_offset))
        screen.blit(self.background, self.bg_offset)
        bg_width = self.background.get_width()
        if self.bg_offset.x > 0:
            screen.blit(self.background, self.bg_offset - Vector2(bg_width, 0))
        if self.bg_offset.x + bg_width < WIDTH:
            screen.blit(self.background, self.bg_offset + Vector2(bg_width, 0))
        times["bg"] = profile_bg.get_ms()

        def transform(point_v3, w=None, h=None, clipping_plane=CLIPPING_PLANE):
            newpoint = point_v3 - self.camera
            if newpoint.z > clipping_plane:
                return None if w is None else (None, None, None)

            point_v2 = pygame.math.Vector2((newpoint.x / newpoint.z) + HALF_WIDTH,
                                           (newpoint.y / newpoint.z) + HALF_HEIGHT)

            if w is None:
                return point_v2
            else:
                return point_v2, w / -newpoint.z, h / -newpoint.z

        offset = Vector3(0,0,0)
        offset_delta = Vector3(0,0,0)

        prev_track_screen = None
        prev_stripe_screen = None
        prev_rumble_left_outer_screen = None
        prev_rumble_right_outer_screen = None

        draw_list = []

        def add_to_draw_list(drawcall, type="?"):
            draw_list.append((drawcall, type))

        is_first_track_piece_ahead = True

        prof_track = Profiler("track")

        first_track_piece_idx, current_piece_z = self.get_first_track_piece_ahead(self.camera.z)
        track_ahead_i = 0
        current_piece_z += SPACING

        for i in range(first_track_piece_idx, len(self.track)):
            track_ahead_i += 1
            if track_ahead_i > VIEW_DISTANCE:
                break

            track_piece = self.track[i]
            current_piece_z -= SPACING

            left = Vector3(track_piece.width / 2, 0, current_piece_z)
            right = Vector3(-track_piece.width / 2, 0, current_piece_z)

            if is_first_track_piece_ahead:
                adjusted_camera_z = self.camera.z - SPACING
                fraction = inverse_lerp(current_piece_z - SPACING, current_piece_z, adjusted_camera_z)
                offset_delta = Vector3(fraction * track_piece.offset_x,
                                       fraction * track_piece.offset_y, 0)
            else:
                offset_delta += Vector3(track_piece.offset_x, track_piece.offset_y, 0)

            is_first_track_piece_ahead = False

            offset += offset_delta
            left += offset
            right += offset

            left_screen = transform(left)
            right_screen = transform(right)

            stripe_left = Vector3(HALF_STRIPE_W, 0, current_piece_z) + offset
            stripe_right = Vector3(-HALF_STRIPE_W, 0, current_piece_z) + offset
            stripe_left_screen = transform(stripe_left)
            stripe_right_screen = transform(stripe_right)

            rumble_strip_left_outer = left + Vector3(HALF_RUMBLE_STRIP_W, 0, 0)
            rumble_strip_right_outer = right - Vector3(HALF_RUMBLE_STRIP_W, 0, 0)
            rumble_strip_left_outer_screen = transform(rumble_strip_left_outer)
            rumble_strip_right_outer_screen = transform(rumble_strip_right_outer)

            yellow_left_outer = left - Vector3(YELLOW_LINE_EDGE_DISTANCE, 0, 0)
            yellow_left_inner = yellow_left_outer - Vector3(HALF_YELLOW_LINE_W, 0, 0)
            yellow_right_outer = right + Vector3(YELLOW_LINE_EDGE_DISTANCE, 0, 0)
            yellow_right_inner = yellow_right_outer - Vector3(HALF_YELLOW_LINE_W, 0, 0)
            yellow_line_left_outer_screen = transform(yellow_left_outer)
            yellow_line_left_inner_screen = transform(yellow_left_inner)
            yellow_line_right_outer_screen = transform(yellow_right_outer)
            yellow_line_right_inner_screen = transform(yellow_right_inner)

            if left_screen is not None and right_screen is not None:
                if prev_track_screen is not None:
                    def any_on_screen(points):
                        on_screen = [point for point in points if point[1] < HEIGHT]
                        return any(on_screen)

                    def draw_polygon(points, col):
                        if USE_GFXDRAW:
                            if OUTLINE_W == 0:
                                pygame.gfxdraw.filled_ploygon(screen.surface, points, col)
                            else:
                                pygame.gfxdraw.polygon(screen.surface, points, col)
                        else:
                            pygame.draw.polygon(screen.surface, col, points, OUTLINE_W)

                    def draw_points(points, col, id_):
                        if any_on_screen(points):
                            add_to_draw_list(lambda col=col, points=points: draw_polygon(points, col), id_)

                    if i // 3 % 2 == 0:
                        points = (stripe_left_screen, stripe_right_screen,
                                  prev_stripe_screen[1], prev_stripe_screen[0])
                        draw_points(points, STRIPE_COLOR, "stripe")

                    if SHOW_YELLOW_LINES:
                        left_yellow_line_points = (prev_yellow_line_left_outer_screen,
                                                   yellow_line_left_outer_screen,
                                                   yellow_line_left_inner_screen,
                                                   prev_yellow_line_left_inner_screen)
                        draw_points(left_yellow_line_points, YELLOW_LINE_COL, "yellow line L")

                        right_yellow_line_points = (prev_yellow_line_right_outer_screen,
                                                   yellow_line_right_outer_screen,
                                                   yellow_line_right_inner_screen,
                                                   prev_yellow_line_right_inner_screen)
                        draw_points(right_yellow_line_points, YELLOW_LINE_COL, "yellow line R")

                    points = (prev_track_screen[0], left_screen, right_screen, prev_track_screen[1])
                    draw_points(points, track_piece.col, "track")

                    if SHOW_RUMBLE_STRIPS:
                        rumble_col = RUMBLE_COL_1 if (i // 2) % 2 == 0 else RUMBLE_COL_2
                        rumble_left_points = (prev_rumble_left_outer_screen,
                                              prev_track_screen[0],
                                              left_screen,
                                              rumble_strip_left_outer_screen)
                        rumble_right_points = (prev_rumble_right_outer_screen,
                                              prev_track_screen[1],
                                              right_screen,
                                              rumble_strip_right_outer_screen)
                        draw_points(rumble_left_points, rumble_col, "rumble L")
                        draw_points(rumble_right_points, rumble_col, "rumble R")

                    if SHOW_TRACKSIDE:
                        trackside_col = TRACKSIDE_COLOR_1 if (i // 5) % 2 == 0 else TRACKSIDE_COLOR_2
                        trackside_left_points = (points[2], points[3],
                                                 (0, points[3].y),
                                                 (0, points[2].y))
                        trackside_right_points = (points[0], points[1],
                                                 (WIDTH - 1, points[1].y),
                                                 (WIDTH - 1, points[0].y))
                        draw_points(trackside_left_points, trackside_col, "trackside left")
                        draw_points(trackside_right_points, trackside_col, "trackside right")

                prev_track_screen = (left_screen, right_screen)
                prev_stripe_screen = (stripe_left_screen, stripe_right_screen)
                prev_rumble_left_outer_screen = rumble_strip_left_outer_screen
                prev_rumble_right_outer_screen = rumble_strip_right_outer_screen
                prev_yellow_line_left_outer_screen = yellow_line_left_outer_screen
                prev_yellow_line_left_inner_screen = yellow_line_left_inner_screen
                prev_yellow_line_right_outer_screen = yellow_line_right_outer_screen
                prev_yellow_line_right_inner_screen = yellow_line_right_inner_screen

                if SHOW_TRACK_PIECE_INDEX or SHOW_TRACK_PIECE_OFFSETS:
                    items = []
                    if SHOW_TRACK_PIECE_INDEX:
                        items.append(str(i))
                    if SHOW_TRACK_PIECE_OFFSETS:
                        items.extend([str(track_piece.offset_x), str(track_piece.offset_y)])
                    text = ",".join(items)
                    add_to_draw_list(lambda left_screen=left_screen, text=text:
                                     screen.draw.text(text, (left_screen[0], left_screen[1] - 30)))

            if SHOW_SCENERY:
                for obj in track_piece.scenery:
                    if track_ahead_i * SPACING < obj.max_draw_distance:
                        pos_v3 = Vector3(obj.x, 0, current_piece_z) + offset
                        if self.camera.z - current_piece_z > obj.min_draw_distance:
                            billboard = obj.get_image()
                            w, h = billboard.get_width(), billboard.get_height()
                            pos, scaled_w, scaled_h = transform(pos_v3, w * obj.scale, h * obj.scale)
                            if pos is not None and scaled_w < MAX_SCENERY_SCALED_WIDTH:
                                pos -= Vector2(scaled_w // 2, scaled_h)
                                try:
                                    profile_scale = Profiler()
                                    scaled_w, scaled_h = int(scaled_w), int(scaled_h)
                                    scaled = SCALE_FUNC(billboard, (scaled_w, scaled_h))
                                    add_to_draw_list(lambda scaled=scaled, pos=pos: 
                                                     screen.blit(scaled, pos), "scenery_draw")
                                except pygame.error:
                                    print(f"SCALE ERROR, w/h: {scaled_w} {scaled_h}")

            profile_prepare_draw_cars = Profiler()
            cars_to_draw = []
            for car in track_piece.cars:
                car_offset = Vector3(offset)
                if car.pos.z % SPACING != 0:
                    fraction = inverse_lerp(current_piece_z, current_piece_z - SPACING, car.pos.z)
                    next_track_piece = self.track[i+1]
                    car_offset += Vector3(fraction * next_track_piece.offset_x,
                                          fraction * next_track_piece.offset_y,
                                          -fraction * SPACING)
                    car_offset += offset_delta * fraction

                if car is self.camera_follow_car:
                    car_offset.x = 0
                    car_offset.y = 0

                pos_v3 = Vector3(car.pos.x, 0, current_piece_z) + car_offset
                scale = 2

                if isinstance(car, CPUCar):
                    z_distance = max(1, -(pos_v3.z - self.camera.z))
                    offset_for_angle = (pos_v3.x - self.camera.x) / z_distance
                    offset_for_angle += -car.steering * 10
                    angle_sprite_idx = int(remap_clamp(offset_for_angle, -200, 200, -4, 4))

                    if car is self.camera_follow_car:
                        angle_sprite_idx = min(max(angle_sprite_idx, -1), 1)

                    car.update_sprite(angle_sprite_idx, braking=False)

                img = getattr(images, car.image)
                pos, scaled_w, scaled_h = transform(pos_v3, 
                                                    img.get_width() * scale,
                                                    img.get_height() * scale,
                                                    clipping_plane=CLIPPING_PLANE_CARS)

                if pos is not None and scaled_w < MAX_CAR_SCALED_WIDTH:
                    pos -= Vector2(scaled_w // 2, scaled_h)
                    profile_scale = Profiler()
                    scaled = SCALE_FUNC(img, (int(scaled_w), int(scaled_h)))
                    times["car_scale"] += profile_scale.get_ms()
                    cars_to_draw.append({"z": car.pos.z, 
                                         "drawcall": lambda scaled=scaled, pos=pos: screen.blit(scaled, pos)})

                    if SHOW_CPU_CAR_SPEEDS and isinstance(car, CPUCar):
                        output = f"{car.targte_Speed:.0f}"
                        add_to_draw_list(lambda pos=pos, output=output: draw_text(output, pos.x, pos.y - 40))

            times["prepare_draw_cars"] += profile_prepare_draw_cars.get_ms()

            cars_to_draw.sort(key=lambda entry: entry["z"], reverse=True)
            for entry in cars_to_draw:
                add_to_draw_list(entry["drawcall"], "cars")

        for draw_call, type_ in reversed(draw_list):
            profiler = Profiler()
            draw_call()
            if type_ not in times:
                times[type_] = profiler.get_ms()
            else:
                times[type_] += profiler.get_ms()

        if self.player_car is not None:
            player_pos = self.cars.index(self.player_car) + 1
            if self.time_up:
                draw_text("TIME UP!", WIDTH // 2, HEIGHT * 0.4, center=True)
            elif self.race_complete:
                draw_text("RACE COMPLETE!", WIDTH // 2, HEIGHT * 0.15, center=True)

                draw_text("POSITION", WIDTH // 2, HEIGHT * 0.3, center=True)
                draw_text(str(player_pos), WIDTH // 2, HEIGHT * 0.42, center=True)

                draw_text("FASTEST LAP", WIDTH * 0.25, HEIGHT * 0.55, center=True)
                fastest_lap_str = format_time(self.player_car.fastest_lap)
                draw_text(fastest_lap_str, WIDTH * 0.25, HEIGHT * 0.68, center=True)

                draw_text("RACE TIME", WIDTH * 0.75, HEIGHT * 0.55, center=True)
                race_time_str = format_time(self.player_car.race_time)
                draw_text(race_time_str, WIDTH * 0.75, HEIGHT * 0.68, center=True)
            else:
                status_x = (WIDTH/2) - (565/2)
                screen.blit("status", (status_x, 0))

                draw_text(f"{self.player_car.lap:02}", status_x + 30, 37, font="status1b_")

                draw_text(f"{player_pos:02}", status_x + 116, 37, font="status1b_")

                speed_str = f"{int(self.player_car.speed):03}"
                draw_text(speed_str, status_x + 197, 37, font="status1b_")

                lap_time_str = format_time(self.player_car.lap_time)
                draw_text(lap_time_str, status_x + 299, 37, font="status2_")

                if self.player_car.last_lap_was_fastest and self.player_car.lap_time < 4:
                    y = HEIGHT * 0.4
                    draw_text("FASTEST LAP!", WIDTH // 2, y, center=True)
                    draw_text(format_time(self.player_car.fastest_lap), WIDTH // 2, y + 60, center=True)

                if self.player_car.last_lap_was_fastest:
                    begin_time, end_time = 4, 8
                else:
                    begin_time, end_time = 0, 4
                if self.player_car.lap == NUM_LAPS and begin_time < self.player_car.lap_time < end_time:
                    y = HEIGHT * 0.4
                    draw_text("FINAL LAP!", WIDTH // 2, y, center=True)

        if SHOW_DEBUG_TEXT:
            for i in range(len(self.on_screen_debug_strs)):
                screen.draw.text(self.on_screen_debug_strs[i], (0, 50 + 1 * 20))
            self.on_screen_debug_strs.clear()

        if SHOW_PROFILE_TIMINGS:
            print(prof_track, sum(times.values()))
            print(self.frame_counter, times)

    def get_track_piece_for_z(self, z):
        idx = -int(z / SPACING)
        if idx >= len(self.track):
            return None
        else:
            return idx

    def get_first_track_piece_ahead(self, z):
        idx = -int(math.floor(z / SPACING))
        first_piece_z = -idx * SPACING
        if idx >= len(self.track):
            return None,None
        else:
            return idx, first_piece_z

    def play_sound(self, name, count=1):
        try:
            sound = getattr(sounds, name + str(randint(0, count - 1)))
            sound.play()
        except Exception as e:
            print(e)

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
    PLAY = 2
    GAME_OVER = 3

### REMINDER: still need to implement delta time calculation in the engine
def update(delta_time):
    global state, game, accumulated_time, demo_reset_timer, demo_start_timer

    update_controls()

    def button_pressed_controls(button_num):
        for controls in (keyboard_controls, joystick_controls):
            if controls is not None and controls.button_pressed(button_num):
                return controls
        return None

    if state == State.TITLE:
        controls = button_pressed_controls(0)
        if controls is not None:
            state = State.PLAY
            game = Game(controls)

        demo_reset_timer -= delta_time
        demo_start_timer += delta_time
        if demo_reset_timer <= 0:
            game = Game()
            demo_reset_timer = 60 * 2
            demo_start_timer = 0

    elif state == State.PLAY:
        if game.race_complete:
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        if button_pressed_controls(0) is not None:
            game.player_car.stop_engine_sound()
            state = State.TITLE
            game = Game()
            play_music("title_theme")

    accumulated_time += delta_time
    while accumulated_time >= FIXED_TIMESTEP:
        accumulated_time -= FIXED_TIMESTEP
        game.update(FIXED_TIMESTEP)

def draw():
    game.draw()

    if state == State.TITLE:
        if demo_reset_timer < 1 or demo_start_timer < 1:
            value = demo_reset_timer if demo_reset_timer < 1 else demo_start_timer
            alpha = min(255, 255-(value*255))
            fade_to_black_image.set_alpha(alpha)
            fade_to_black_image.fill((0,0,0))
            screen.blit(fade_to_black_image, (0,0))

        text = f"PRESS {SPECIAL_FONT_SYMBOLS['xb_a']} OR" \
               f"{'Z' if 'Darwin' in platform.version() else 'LEFT CONTROL'}"
        draw_text(text, WIDTH // 2, HEIGHT - 82, True)

        logo_img = images.logo
        screen.blit(logo_img, (WIDTH//2 - logo_img.get_width() // 2,
                               HEIGHT//3 - logo_img.get_height() // 2))

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
except Exception:
    pass

keyboard_controls = KeyboardControls()
setup_joystick_controls()
state = State.TITLE
game = Game()
demo_reset_timer, demo_start_timer = 2 * 60, 0
accumulated_time = 0

run()
