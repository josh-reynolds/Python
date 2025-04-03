import os
import sys
import xml.etree.ElementTree as ET
from enum import Enum
from random import randint
import pygame
from pygame import Rect
from engine import *

WIDTH = 825
HEIGHT = 550
TITLE = "Huevos"

LEVEL_SEQUENCE = ["starter1.tmx", "starter2.tmx", "starter3.tmx", "starter4.tmx",
                  "forest1.tmx", "forest2.tmx", "forest3.tmx", "forest4.tmx", "forest9.tmx",
                  "castle1.tmx", "castle2.tmx", "castle3.tmx", "castle4.tmx", "castle5.tmx",
                  "castle6.tmx", "castle7.tmx", "castle8.tmx", "forest5.tmx", "forest6.tmx",
                  "forest7.tmx", "forest8.tmx"]

GRID_BLOCK_SIZE = 25
LEVEL_Y_BOUNDARY = -100
INITIAL_LEVEL_CYCLE = 0
INITIAL_TIME_REMAINING = 15
INITIAL_PICKUP_TIME_BONUS = 2
STOMP_ENEMY_TIME_BONUS = 3
COYOTE_TIME = 6
JUMP_VEL_Y = -10
WALL_JUMP_X_VEL = 8
WALL_JUMP_COYOTE_TIME = 15
CACHE_JUMP_INPUT_TIME = 5

PLAYER_WIDTH = 20
PLAYER_HEIGHT = 40

ANCHOR_CENTER = ("center", "center")
ANCHOR_CENTER_BOTTOM = ("center", "bottom")
ANCHOR_PLAYER = ("center", 60)
ANCHOR_FLAME = ("center", 78)
ANCHOR_FLAME_DASH = ("center", 130)

class Biome(Enum):
    FOREST = 0
    CASTLE = 1

ENEMY_SPRITE_NAMES = {Biome.CASTLE: ["robot0", "robot1", "robot2", "robot3"], 
                      Biome.FOREST: ["fly", "mghost", "triffid", "bigbloom"]}

ENEMY_TYPES_FLYING = {Biome.CASTLE: [True, True, False, False],
                      Biome.FOREST: [True, True, False, True]}

ENEMY_TYPES_WIDTH_OVERRIDES = {Biome.CASTLE: [30, 50, 48, 50],
                               Biome.FOREST: [30, 50, 50, 50]}
ENEMY_TYPES_HEIGHT_OVERRIDES = {Biome.CASTLE: [40, 40, 60, 120],
                                Biome.FOREST: [30, 65, 70, 90]}

ENEMY_TYPES_ANCHOR_POINTS = {Biome.CASTLE: [("center", 40),("center", 40),("center", 95),("center", "bottom")],
                             Biome.FOREST: [("center", 60)] + [ANCHOR_CENTER_BOTTOM] * 3}

ENEMY_TYPES_HEALTH = [1, 3, 1, 3]
ENEMY_TYPES_SPEED = [2, 1, 2, 1]

REPLAY_FILENAME = 'replays'
MAX_REPLAYS = 10

def move_towards(n, target, speed):
    if n < target:
        return min(n + speed, target)
    else:
        return max(n - speed, target)

def sign(x):
    if x == 0: 
        return 0
    else:
        return -1 if x < 0 else 1

class KeyboardControls:
    NUM_BUTTONS = 2

    def __init__(self):
        self.previously_down = [False for i in range(KeyboardControls.NUM_BUTTONS)]
        self.is_pressed = [False for i in range(KeyboardControls.NUM_BUTTONS)]

    def update(self):
        for button in range(KeyboardControls.NUM_BUTTONS):
            button_down = self.button_down(button)
            self.is_pressed[button] = button_down and not self.previously_down[button]
            self.previously_down[button] = button_down

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
            return keyboard.space
        else:
            return keyboard.z

    def button_name(self, button):
        if button == "dash":
            return "Z"
        elif button == "jump":
            return "SPACE"

    def button_pressed(self, button):
        return self.is_pressed[button]

class Gem(Actor):
    next_type = 1

    def __init__(self, pos):
        super().__init__("blank", pos, ANCHOR_CENTER_BOTTOM)
        self.type = Gem.next_type
        Gem.next_type += 1
        if Gem.next_type >= 5:
            Gem.next_type = 1
        self.collected = False

    def update(self):
        if game.player is not None and game.player.collidepoint(self.center):
            game.gain_time(game.time_pickup_bonus, self.centerx, self.centery)
            game.play_sound("collect")
            self.collected = True
        anim_frame = str((game.timer // 6) % 4)
        self.image = f"gem{self.type}_{anim_frame}"

    @staticmethod
    def new_game():
        Gem.next_type = 1

class Door(Actor):
    def __init__(self, pos, biome="castle", variant=0, already_open=False):
        self.biome = biome
        self.variant = variant
        self.opening = already_open
        self.last_frame = 15 if biome == "castle" else 13
        self.frame = self.last_frame if already_open else 0
        super().__init__(f"door_{biome}_{variant}_{self.frame}", pos, anchor=(0,0))

    def update(self):
        pass   ###
    def open(self):
        pass   ###
    def is_fully_open(self):
        pass   ###

class Animation(Actor):
    def __init__(self, pos, image_format_str, num_frames, frame_interval,
                 anchor=ANCHOR_CENTER, initial_delay=0, rise_time=-1):
        super().__init__("blank", pos, anchor)
        self.image_format_str = image_format_str
        self.num_frames = num_frames
        self.frame_interval = frame_interval
        self.timer = -initial_delay
        self.rise_time = rise_time
        self.update_image()

    def update(self):
        self.timer += 1
        self.update_image()
        if self.rise_time > -1 and self.timer > self.rise_time:
            self.y -= 1

    def update_image(self):
        if self.timer < 0:
            self.image = "blank"
        else:
            frame = min(self.timer // self.frame_interval, self.num_frames - 1)
            self.image = self.image_format_str.format(frame)

    def finished(self):
        return self.timer // self.frame_interval >= self.num_frames

class DashTrail(Animation):
    def __init__(self, pos, image):
        super().__init__(pos, image + "_trail_{0}", 6, 5, ANCHOR_PLAYER)

class CollideActor(Actor):
    def __init__(self, pos, anchor=ANCHOR_CENTER):
        super().__init__("blank", pos, anchor)

    def move(self, dx, dy, speed):
        new_x, new_y = self.x, self.y

        for i in range(speed):
            new_x, new_y = new_x + dx, new_y + dy
            rect = self.get_rect(new_x, new_y)
            if game.position_blocked(rect):
                return True

            self.pos = new_x, new_y

        return False

    def get_rect(self, center_x=None, bottom_y=None):
        if center_x is None:
            center_x = self.x
        if bottom_y is None:
            bottom_y = self.y
        w, h = self.get_collideable_width(), self.get_collideable_height()
        return Rect(center_x - (w // 2), bottom_y - h, w, h)

    def get_collideable_width(self):
        # overriden for Player and Enemy
        image_surface = getattr(images, self.image)
        return image_surface.get_width()

    def get_collideable_height(self):
        # overriden for Player and Enemy
        image_surface = getattr(images, self.image)
        return image_surface.get_height()

class GravityActor(CollideActor):
    MAX_FALL_SPEED = 7

    class FallState(Enum):
        LANDED = 0
        FALLING = 1
        JUMPING = 2
        WALL_JUMPING = 3

    def __init__(self, pos, gravity_enabled=True, anchor=ANCHOR_CENTER_BOTTOM):
        super().__init__(pos, anchor)

        self.gravity_enabled = gravity_enabled
        self.vel_y = 0
        self.fall_state = GravityActor.FallState.FALLING
        self.lower_gravity_timer = 0

    def update(self, detect=True):
        if not self.gravity_enabled:
            return

        self.lower_gravity_timer -= 1

        if game.timer % (3 if self.lower_gravity_timer > 0 else 2) == 0:
            self.vel_y = min(self.vel_y + 1, GravityActor.MAX_FALL_SPEED)

        if detect and self.vel_y != 0:
            if self.fall_state == GravityActor.FallState.LANDED:
                self.fall_state = GravityActor.FallState.FALLING
            if self.vel_y != 0 and self.move(0, sign(self.vel_y), abs(self.vel_y)):
                if self.vel_y > 0:
                    self.vel_y = 0
                    self.fall_state = GravityActor.FallState.LANDED
        else:
            self.y += self.vel_y

    def landed(self):
        return self.fall_state == GravityActor.FallState.LANDED

class Player(GravityActor):
    DASH_TIME = 18
    DASH_SPEED = 10
    DASH_PAUSE_TIME = 5
    DASH_TRAIL_INTERVAL = 3
    DASH_TIMER_TRAIL_CUTOFF = -10
    MAX_X_RUN_SPEED = 5

    def __init__(self, controls):
        super().__init__((0,0), anchor=ANCHOR_PLAYER)

        self.controls = controls
        self.flame = Actor("flame_stand_0", self.pos, anchor=ANCHOR_FLAME)
        self.vel_x = 0
        self.facing_x = 1
        self.hurt = False
        self.dash_timer = Player.DASH_TIMER_TRAIL_CUTOFF   # counts down
        self.dash_animation_timer = 0                      # counts up
        self.dash_allowed = False
        self.grabbed_wall = 0
        self.coyote_time = 0
        self.fall_timer = 0
        self.wall_jump_coyote_time = 0
        self.cached_jump_input_timer = 0
        self.enemy_stomped_timer = 0
        self.change_direction_timer = 0
        self.last_dash_sprite = "dash_horizontal_0_0"  # used for dash trails
        self.replay_data = []

    def new_level(self, start_pos):
        self.start_pos = start_pos
        self.reset()

    def reset(self):
        self.pos = self.start_pos
        self.vel_x = 0
        self.vel_y = 0
        self.facing_x = 1
        self.hurt = False
        self.dash_timer = Player.DASH_TIMER_TRAIL_CUTOFF
        self.gravity_enabled = True
        self.grabbed_wall = 0
        self.coyote_time = 0
        self.wall_jump_coyote_time = 0
        self.cached_jump_input_timer = 0
        self.enemy_stomped_timer = 0

        if game is not None:
            for enemy in game.enemies:
                if self.distance_to(enemy) < 150:
                    enemy.destroy()
                    game.play_sound("enemy_death", 5)

    def hit_test(self, other):
        return self.get_rect(self.x, self.y).colliderect(other.get_rect()) and not self.hurt

    def get_colliding_enemies(self):
        return [enemy for enemy in game.enemies if not enemy.dying and self.hit_test(enemy)]

    def update(self):
        was_landed = self.landed()
        super().update(not self.hurt)

        if was_landed and not self.landed():
            self.coyote_tme = COYOTE_TIME
            self.fall_timer = 0

        if self.top >= HEIGHT:
            self.reset()

        stomped_any = False
        for enemy in self.get_colliding_enemies():
            enemy_rectc = enemy.get_rect()
            threshold = enemy_rect.top + (enemy_rect.bottom - enemy_rect.top) * \
                    (0.5 if self.vel_y > 0 else 0.2)
            if self.y < threshold or self.stomped_last_frame:
                enemy.stomped()
                stomped_any = True
                self.vel_y = -6
                self.enemy_stomped_timer = 3
                self.dash_allowed = True
            else:
                self.hurt = True
                self.vel_y = -12
                self.fall_state = GravityActor.FallState.FALLING
                self.fall_timer = 0
                self.dash_timer = Player.DASH_TIMER_TRAIL_CUTOFF
                game.play_sound("player_death")
                game.animations.append(Animation(self.pos, "loselife_{0}", 8, 4))
                break

        self.stomped_last_frame = stomped_any

        if self.landed():
            self.dash_allowed = True

        self.dash_timer -= 1
        self.dash_animation_timer += 1
        self.cached_jump_input_timer -= 1
        self.coyote_time -= 1
        self.wall_jump_coyote_time -= 1

        if self.dash_timer > Player.DASH_TIMER_TRAIL_CUTOFF:
            if self.dash_timer % Player.DASH_TRAIL_INTERVAL == 0:
                game.animations.append(DashTrail(self.pos, self.last_dash_sprite))

        dx = 0 # x direction we tried to move this frame

        jump_pressed = self.controls.button_pressed(0)

        if self.hurt:
            self.gravity_enabled = True
            if self.top >= HEIGHT:
                self.hurt = False

        elif self.dash_timer > 0:
            if self.dash_timer < Player.DASH_TIME:
                if self.dash_timer % Player.DASH_TRAIL_INTERVAL == 0:
                    game.animations.append(DashTrail(self.pos, self.last_dash_sprite))

                self.move(0, sign(self.vel_y), abs(self.vel_y))

                if self.move(sign(self.vel_x), 0, abs(self.vel_x)) and self.vel_y >= 0:
                    self.dash_timer = 0
                    self.grabbed_wall = self.facing_x
        else:
            dx = self.controls.get_x()

            def jump():
                self.vel_y = JUMP_VEL_Y
                self.fall_state = GravityActor.FallState.JUMPING
                self.coyote_time = 0
                self.cached_jump_input_timer = 0
                self.lower_gravity_timer = 5
                self.fall_timer = 0
                game.play_sound("jump")

            def wall_jump(wall_direction):
                self.vel_y = JUMP_VEL_Y
                self.fall_state = GravityActor.FallState.WALL_JUMPING
                self.vel_x = -wall_direction * WALL_JUMP_X_VEL
                self.facing_x = -wall_direction
                self.grabbed_wall = 0
                self.previous_grabbed_wall = 0
                self.wall_jump_coyote_time = 0
                self.cached_jump_input_timer = 0
                self.fall_timer = 0
                game.play_sound("jump")

            if self.grabbed_wall != 0:
                self.gravity_enabled = False

                if jump_pressed or self.cached_jump_input_timer > 0:
                    wall_jump(self.grabbed_wall)
                elif dx == -self.grabbed_wall:
                    # pushing away from wall
                    self.previous_grabbed_wall = self.grabbed_wall
                    self.wall_jump_coyote_time = WALL_JUMP_COYOTE_TIME
                    self.grabbed_wall = 0
                else:
                    # wall slide
                    rect = self.get_rect(self.x + self.grabbed_wall, self.y)
                    if self.move(0, 1, 1) or not game.position_blocked(rect):
                        self.grabbed_wall = 0
            else:
                # not grabbing a wall
                if jump_pressed and self.wall_jump_coyote_time > 0:
                    wall_jump(self.previous_grabbed_wall)
                else:
                    # normal movement
                    self.gravity_enabled = True
                    if dx == 0:
                        self.vel_x = move_towards(self.vel_x, 0, 1)
                    else:
                        self.facing_x = dx
                        self.vel_x = move_towards(self.vel_x, Player.MAX_X_RUN_SPEED * dx, 1)

                    # check for grabbing a wall
                    if self.vel_x != 0 and self.move(sign(self.vel_x), 0, abs(self.vel_x)) \
                            and self.vel_y > 0:
                                self.grabbed_wall = sign(self.vel_x)
                                self.vel_x = 0

                    if (jump_pressed or self.cached_jump_input_timer > 0) \
                            and (self.landed() or self.coyote_time > 0):
                                jump()

                    elif jump_pressed and not self.landed():
                        self.cached_jump_input_timer = CACHE_JUMP_INPUT_TIME

                    elif not self.landed() and self.vel_y < 0 and self.dash_timer < -10 \
                            and not self.controls.button_down(0) \
                            and self.enemy_stomped_timer <= 0:
                                self.vel_y = min(self.vel_y + 1, 0)

                    if self.dash_allowed and self.controls.button_pressed(1):
                        dy = self.controls.get_y()
                        if dx != 0 or dy != 0:
                            v = pygame.math.Vector2(dx,dy).normalize() * Player.DASH_SPEED
                            self.vel_x = int(v.x)
                            self.vel_y = int(v.y)
                            self.gravity_enabled = False
                            self.dash_allowed = False
                            self.dash_tmer = Player.DASH_TIME + Player.DASH_PAUSE_TIME
                            self.dash_animation_timer = 0
                            self.fall_state = GravityActor.FallState.FALLING
                            self.wall_jump_coyote_time = 0
                            game.play_sound("jump_long", 5)

        if sign(dx) != sign(self.vel_x) and self.dash_timer <= 0:
            self.change_direction_timer = 5
        else:
            self.change_direction_timer -= 1

        self.determine_sprite(dx)

        if not self.landed() and self.dash_timer <= 0:
            self.fall_timer += 1

        self.replay_data.append( (self.pos, game.level_index, self.image) )

    def determine_sprite(self, dx):
        self.image = self.flame.image = "blank"
        self.flame.anchor = ANCHOR_FLAME
        if not self.hurt or game.timer % 2 == 1:
            dir_index = "1" if self.facing_x < 0 else "0"
            if self.hurt:
                frame = min(self.fall_timer // 8, 5)
                self.image = f"die_{frame}"
                self.flame_image = "blank"

            elif self.grabbed_wall != 0 and self.vel_y >= 0:
                self.image = f"climb_{dir_index}_1"
                self.flame.image = f"flame_climb_{dir_index}_1"

            elif not self.landed():
                if self.fall_state == GravityActor.FallState.JUMPING:
                    frame = min(self.fall_timer // 3, 5)
                    flame_frame = min(self.fall_timer // 3, 5) + 1
                    self.image = f"jump_{dir_index}_{frame}"
                    self.flame.image = f"flame_jump_{dir_index}_{flame_frame}"
                elif self.fall_state == GravityActor.FallState.WALL_JUMPING:
                    frame = min(self.fall_timer // 8, 2)
                    flame_frame = min(self.fall_timer // 4, 6)
                    self.image = f"wall_jump_{dir_index}_{frame}"
                    self.flame.image = f"flame_wall_jump_{dir_index}_{flame_frame}"
                elif self.dash_timer > 0:
                    if self.dash_animation_timer < 4:
                        flame_frame = self.dash_animation_timer // 2
                        self.image = self.last_dash_sprite = "dash_start_" + dir_index
                        self.flame.image = f"flame_dash_start_{dir_index}_{flame_frame}"
                        self.flame.anchor = ANCHOR_FLAME
                    else:
                        timer = self.dash_animation_timer - 4
                        frame = min(timer // 3, 2)
                        flame_frame = min(timer // 3, 7)
                        sprite = "dash_"
                        if self.vel_y < 0:
                            sprite += "up_"
                        elif self.vel_y > 0:
                            sprite += "down_"
                        if self.vel_x != 0:
                            sprite += "horizontal_"
                        self.image = self.last_dash_sprite = f"{sprite}{dir_index}_{frame}"
                        self.flame.image = f"flame_{sprite}{dir_index}_{flame_frame}"
                        self.flame.anchor = ANCHOR_FLAME_DASH
                else:
                    frame = min(self.fall_timer // 8, 1)
                    flame_frame = min(self.fall_timer // 8, 1) + 4
                    self.image = f"fall_{dir_index}_{frame}"
                    self.flame.image = f"flame_wall_jump_{dir_index}_{flame_frame}"
            
            elif dx == 0:
                self.image = "stand_front"
                self.flame.image = f"flame_stand_{(game.timer // 4) % 8}"

            elif self.change_direction_timer > 0:
                self.image = f"change_dir_{dir_index}_0"
                self.flame.image = f"flame_change_dir_{dir_index}_{(game.timer // 4) % 3}"

            else:
                frame = (game.timer // 4) % 8
                self.image = f"run_{dir_index}_{frame}"
                self.flame.image = f"flame_run_{dir_index}_{(game.timer // 4) % 8}"

    def draw(self):
        super().draw()
        self.flame.pos = self.pos
        self.flame.draw()

    def get_collideable_width(self):
        return PLAYER_WIDTH

    def get_collideable_height(self):
        return PLAYER_HEIGHT

class GhostPlayer(Actor):
    def __init__(self, replay_data):
        super().__init__("blank", replay_data[0][0], ANCHOR_PLAYER)
        self.replay_data = replay_data
        self.replay_frame = 0
        self.level = 0

    def update(self):
        self.replay_frame += 1
        if self.replay_frame < len(self.replay_data):
            self.pos, self.level, sprite = self.replay_data[self.replay_frame]
            if sprite == "blank":
                self.image = "blank"
            else:
                self.image = "ghost_" + sprite

    def draw(self):
        if self.level == game.level_index:
            super().draw()

class Enemy(GravityActor):
    def __init__(self, pos, type_, biome, direction_x=1, appearance_count=1):
        super().__init__(pos, gravity_enabled=not ENEMY_TYPES_FLYING[biome][type_],
                         anchor=ENEMY_TYPES_ANCHOR_POINTS[biome][type_])
        self.direction_x = direction_x
        self.type = type_
        self.biome = biome
        self.health = ENEMY_TYPES_HEALTH[type_]
        self.speed = ENEMY_TYPES_SPEED[type_]
        self.dir_y = 1 if appearance_count >= 3 and not self.gravity_enabled else 0
        self.use_directional_sprites = (biome == Biome.CASTLE and self.type >= 2) \
                or (biome == Biome.FOREST and self.type < 1)
        self.dying = False
        self.stompd_timer = 0

    def update(self):
        super().update(detect=not self.dying)

        if not self.dying:
            self.stomped_timer -= 1
            if not self.gravity_enabled or self.fall_state != GravityActor.FallState.FALLING:
                if self.move(self.direction_x, 0, self.speed):
                    self.direction_x = -self.direction_x
                if self.dir_y != 0 and self.move(0, self.dir_y, self.speed):
                    self.dir_y = -self.dir_y

        image = ENEMY_SPRITE_NAMES[self.biome][self.type]
        if self.use_directional_sprites:
            direction_idx = "1" if self.direction_x > 0 else "0"
            image += "_" + str(direction_idx)
        image += "_" + str((game.timer // 4) % 8)
        if self.stomped_timer > 0 or self.dying:
            image += "_hit"
        self.image = image

    def stomped(self):
        if self.stomped_timer <= 0:
            self.health -= 1
            if self.health <= 0:
                self.destroy()
                game.play_sound("enemy_death", 5)
            else:
                game.play_sound("enemy_take_damage", 5)
        self.stomped_timer = 2

    def destroy(self):
        self.dying = True
        self.gravity_enabled = True
        explosion_sprite = "explosion" if self.type > 1 else "air_explosion"
        game.animations.append(Animation(self.pos, explosion_sprite + "_{0}", 12, 4, ANCHOR_CENTER_BOTTOM))
        game.gain_time(STOMP_ENEMY_TIME_BONUS, self.centerx, self.centery)

    def get_collideable_width(self):
        return ENEMY_TYPES_WIDTH_OVERRIDES[self.biome][self.type]

    def get_collideable_height(self):
        return ENEMY_TYPES_HEIGHT_OVERRIDES[self.biome][self.type]

class Game:
    def __init__(self, player=None, replays=None):
        self.player = player

        Gem.new_game()

        self.ghost_players = []
        if replays is not None:
            for replay in replays:
                self.ghost_players.append(GhostPlayer(replay))

        self.timer = 0
        self.time_remaining = INITIAL_TIME_REMAINING * 60
        self.time_pickup_bonus = INITIAL_PICKUP_TIME_BONUS
        self.gained_time_timer = 0
        self.level_index = (INITIAL_LEVEL_CYCLE * len(LEVEL_SEQUENCE)) - 1
        self.level_text = ""
        self.grid = None
        self.tileset_image = None
        self.background_image = None
        self.background_y_offset = 0

        self.next_level()

    def next_level(self):
        self.level_index += 1

        if self.level_index != 0 and self.level_index % len(LEVEL_SEQUENCE) == 0:
            if self.time_pickup_bonus > 1:
                self.time_pickup_bonus -= 1
            elif self.time_pickup_bonus == 1:
                self.time_pickup_bonus = 0.5

        self.block_rects = []
        self.doors = []
        self.gems = []
        self.enemies = []
        self.animations = []
        self.level_text = ""
        self.exit_open = False

        filename = LEVEL_SEQUENCE[self.level_index % len(LEVEL_SEQUENCE)]
        player_start_pos = self.load_level(filename)

        if self.player is not None:
            self.player.new_level(player_start_pos)

        self.generate_block_rects()

        if self.player:
            self.player.reset()

        self.play_sound("new_wave")

    def load_level(self, filename):
        player_start_pos = (0,0)
        level_cycle = self.level_index // len(LEVEL_SEQUENCE)

        path = os.path.join(sys.path[0], "tilemaps")

        map_tree = ET.parse(os.path.join(path, filename))
        map_root = map_tree.getroot()

        properties_node = map_root.find("properties")
        bg = properties_node.find("./property[@name='Background']").attrib["value"]
        self.background_image = bg
        offset_node = properties_node.find("./property[@name='Background Offset Y']")
        self.background_y_offset = int(offset_node.attrib["value"]) if offset_node is not None else 0

        biome_node = properties_node.find("./property[@name='biome']")
        biome_name = biome_node.attrib["value"] if biome_node is not None else ""
        biome = Biome[biome_name.upper()]

        self.level_text = "LEVEL " + str(self.level_index + 1)

        tutorial_text_node = properties_node.find("./property[@name='TutorialText']")
        if self.player is not None and tutorial_text_node is not None:
            tutorial_text = tutorial_text_node.attrib["value"]
            if level_cycle == 0 and len(tutorial_text) > 0:
                dash_button_name = self.player.controls.button_name("dash")
                jump_button_name = self.player.controls.button_name("jump")
                self.level_text = tutorial_text.replace("{DASH}", dash_button_name)
                self.level_text = self.level_text.replace("{JUMP}", jump_button_name)

        layer_node = map_root.find("layer")
        map_w = int(layer_node.attrib.get("width"))
        map_h = int(layer_node.attrib.get("height"))
        map_data = layer_node.find("data").text.split(",")

        self.grid = []
        for row in range(map_h):
            row0_idx = row * map_w
            current_row = [int(tile)-1 for tile in map_data[row0_idx:row0_idx+map_w]]
            self.grid.append(current_row)

        object_group_node = map_root.find("objectgroup")
        if object_group_node is not None:
            for obj_node in object_group_node.findall("object"):
                object_name = obj_node.attrib["name"]
                object_pos = (int(float(obj_node.attrib["x"])),
                              int(float(obj_node.attrib["y"])))

                if object_name == "PlayerStart":
                    player_start_pos = object_pos

                elif object_name == "Gem":
                    self.gems.append(Gem(object_pos))

                elif "Enemy" in object_name:
                    enemy_level_cycle = int(object_name[-1])
                    appearance_count = (level_cycle - enemy_level_cycle) + 1
                    if appearance_count >= 1:
                        facing = 1 if object_name[-3] == "R" else -1
                        enemy_type = int(object_name[-2])
                        self.enemies.append(Enemy(object_pos, enemy_type, biome, facing, appearance_count))

                elif "Door" in object_name:
                    variant_node = obj_node.find("./properties/property[@name='Variant']")
                    biome_node = obj_node.find("./properties/property[@name='Biome']")
                    variant = variant_node.attrib["value"] if variant_node is not None else 0
                    door_biome = biome_node.attrib["value"] if biome_node is not None else biome_name
                    entrance = "Entrance" in object_name
                    self.doors.append(Door(object_pos, door_biome, variant, entrance))

        tileset_filename = map_root.find("tileset").attrib.get("source")

        self.collision_tiles = set()
        tileset_xml = ET.parse(os.path.join(path, tileset_filename))
        for tile_node in tileset_xml.getroot().findall("tile"):
            self.collision_tiles.add(int(tile_node.attrib["id"]))

        tileset_image_filename = tileset_xml.getroot().find("image").attrib["source"]
        if tileset_image_filename not in tileset_images:
            tileset_images[tileset_image_filename] = pygame.image.load(os.path.join(path, tileset_image_filename))
        self.tileset_image = tileset_images[tileset_image_filename]

        return player_start_pos

    def generate_block_rects(self):
        self.block_rects = []
        current_rect = None

        def add():
            nonlocal current_rect
            self.block_rects.append(current_rect)
            current_rect = None

        for gy in range(len(self.grid)):
            row = self.grid[gy]
            for gx in range(len(row)):
                if row[gx] in self.collision_tiles:
                    pos_x = gx * GRID_BLOCK_SIZE
                    pos_y = gy * GRID_BLOCK_SIZE
                    if current_rect is None:
                        current_rect = Rect(pos_x,pos_y, GRID_BLOCK_SIZE, GRID_BLOCK_SIZE)
                    else:
                        current_rect.w += GRID_BLOCK_SIZE
                elif current_rect is not None:
                    add()
            if current_rect is not None:
                add()

        def find_equal_width_block_below(current):
            result = [rect for rect in self.block_rects if rect.x == current.x
                      and rect.w == current.w and rect.y == current.y + current.h]
            return result[0] if len(result) > 0 else None

        any_found = True
        while any_found:
            any_found = False
            for current in self.block_rects:
                equal_below = find_equal_width_block_below(current)
                if equal_below is not None:
                    current.h += equal_below.h
                    self.block_rects.remove(equal_below)
                    any_found = True
                    break

        for rect in self.block_rects:
            if rect.top == 0:
                height = rect.height
                rect.top = LEVEL_Y_BOUNDARY
                rect.height = height + -LEVEL_Y_BOUNDARY

    def update(self):
        self.timer += 1
        self.gained_time_timer -= 1

        if self.time_remaining > 0:
            self.time_remaining -= 1

        for obj in [self.player] + self.doors + self.animations + self.gems + self.enemies + self.ghost_players:
            if obj:
                obj.update()

        self.enemies = [enemy for enemy in self.enemies if enemy.top < HEIGHT]
        self.animations = [anim for anim in self.animations if not anim.finished]
        self.gems = [gem for gem in self.gems if not gem.collected]

        if self.player is not None:
            if self.exit_open:
                if self.player.centerx > WIDTH:
                    self.next_level()

            elif len(self.gems) == 0:
                self.exit_open = True
                for door in self.doors:
                    door.open()

    def draw(self):
        screen.blit(self.background_image, (0, self.background_y_offset))

        tileset_w = self.tileset_image.get_width()
        tileset_grid_w = tileset_w // GRID_BLOCK_SIZE
        for row_y in range(len(self.grid)):
            row = self.grid[row_y]
            x = 0
            for tile in row:
                if tile >= 0:
                    tileset_grid_y = tile // tileset_grid_w
                    tileset_grid_x = tile % tileset_grid_w
                    tile_rect = Rect(tileset_grid_x * GRID_BLOCK_SIZE,
                                     tileset_grid_y * GRID_BLOCK_SIZE,
                                     GRID_BLOCK_SIZE, GRID_BLOCK_SIZE)
                    screen.surface.blit(self.tileset_image,
                                        (x, row_y * GRID_BLOCK_SIZE), area=tile_rect)
                    x += GRID_BLOCK_SIZE

        for obj in self.ghost_players + self.doors + self.animations + [self.player] \
                + self.gems + self.enemies:
                    if obj is not None:
                        obj.draw()

        self.draw_ui()

    def draw_ui(self):
        pygame.draw.rect(screen.surface, (0,54,255), Rect(0,500,WIDTH,5))
        screen.blit("text_area_frame", (0, 500))
        draw_text(self.level_text, WIDTH // 2, 508, align=TextAlign.CENTER)

        screen.blit("status_back", (WIDTH // 2 - 297 // 2, 0))

        font = "font" if self.gained_time_timer < 0 else "fontbr"
        draw_text(f"{self.time_remaining / 60:.1f}", WIDTH // 2, 10, align=TextAlign.CENTER, font=font)

    def gain_time(self, time, x, y):
        game.time_remaining += time * 60
        time_added_id = "half" if time == 0.5 else str(time)
        format_str = "timer_plus" + time_added_id + "_{0}"
        game.animations.append(Animation((x,y), format_str, 14, 4, initial_delay=5, rise_time=34))
        game.animations.append(Animation((x,y), "pickup_{0}", 8, 4))
        self.gained_time_timer = 20

    def position_blocked(self, rect):
        for block_rect in self.block_rects:
            if rect.colliderect(block_rect):
                return True

        for door in self.doors:
            if not door.is_fully_open() and door.colliderect(rect):
                return True

        if rect.left <= 0 or rect.top < LEVEL_Y_BOUNDARY:
            return True

        return False

    def play_sound(self, name, count=1):
        if self.player:
            try:
                sound = getattr(sounds, name + str(randint(0, count - 1)))
                sound.play()
            except Exception as e:
                print(e)

def get_char_image_and_width(char, font):
    if char == " ":
        return None, 22
    else:
        image = getattr(images, f"{font}{ord(char):03d}")
        return image, image.get_width()

def text_width(text, font):
    return sum([get_char_image_and_width(c, font)[1] for c in text])

class TextAlign(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

def draw_text(text, x, y, align=TextAlign.LEFT, font="font"):
    if align == TextAlign.CENTER:
        x -= text_width(text, font) // 2
    elif align == TextAlign.RIGHT:
        x -= text_width(text, font)

    for char in text:
        image, width = get_char_image_and_width(char, font)
        if image is not None:
            screen.blit(image, (x, y))
        x += width

class State(Enum):
    TITLE = 1
    CONTROLS = 2
    PLAY = 3
    GAME_OVER = 4

def get_save_folder():
    current_working_folder = os.getcwd()
    home_folder = os.path.expanduser('~')
    if current_working_folder != home_folder:
        return sys.path[0]
    else:
        path = os.path.expanduser('~/.code-the-classics-vol-2')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

def save_replays(replays):
    try:
        with open(os.path.join(get_save_folder(), REPLAY_FILENAME), "w") as file:
            for replay in replays:
                line = ""
                for entry in replay:
                    line += f"{int(entry[0][0])},{int(entry[0][1])},{entry[1]},{entry[2]};"
                file.write(line[0:-1] + "\n")
    except Exception as e:
        print(f"Error while saving replays: {e}")

def load_replays():
    replays = []
    try:
        path = os.path.join(get_save_folder(), REPLAY_FILENAME)
        if os.path.exists(path):
            with open(path) as file:
                for line in file:
                    current_replay = []
                    line = line.rstrip()
                    entries = line.split(";")
                    for entry in entries:
                        elements = entry.split(",")
                        pos = (float(elements[0]), float(elements[1]))
                        current_replay.append( (pos, int(elements[2]), elements[3]) )
                    replays.append(current_replay)
    except Exception as e:
        print(f"Error while loading replays: '{e}'. Replay data will be reset")
        return [], 0

    high_score = 0 if len(replays) == 0 else len(max(replays, key=lambda replay: len(replay)))
    return replays, high_score

def update():
    global state, game, high_score, game_over_timer, all_replays, total_frames

    total_frames += 1
    keyboard_controls.update()

    def button_pressed_controls(button_num):
        for controls in (keyboard_controls,):
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
            game = Game(Player(controls), all_replays)
            play_music("ingame_theme", 0.2)

    elif state == State.PLAY:
        if game.time_remaining <= 0:
            game.play_sound("gameover")
            state= State.GAME_OVER
            game_over_timer = 0

            all_replays.append(game.player.replay_data)

            if len(all_replays) > MAX_REPLAYS:
                all_replays.sort(key=lambda replay: len(replay), reverse=True)
                all_replays = all_replays[:MAX_REPLAYS]

            save_replays(all_replays)
        else:
            game.update()

    elif state == State.GAME_OVER:
        game_over_timer += 1
        if game_over_timer > 60 and keyboard_controls.button_pressed(0) is not None:
            if game.timer > high_score:
                high_score = game.timer
            state = State.TITLE
            play_music("title_theme")

def draw():
    if state == State.TITLE:
        screen.blit("title", (0,0))
        screen.blit("press_to_start", (0,0))
        anim_frame = (total_frames // 6) % 11
        screen.blit("start" + str(anim_frame), (WIDTH//2 - 150, 360))

    elif state == State.CONTROLS:
        screen.fill((0,0,0))
        screen.blit("controls", (0,0))

    elif state == State.PLAY:
        game.draw()

    elif state == State.GAME_OVER:
        screen.fill((0, 54, 255))

        anim_frame = (total_frames // 5) % 14
        screen.blit(f"gameover{anim_frame}", (WIDTH//2 - 625//2, 100))

        seconds = int(game.timer / 60)
        if seconds >= 60:
            screen.blit("survived_for_mins_seconds", (0,0))
            draw_text(f"{seconds//60}", 180, 270, align=TextAlign.RIGHT, font="fontlrg")
            draw_text(f"{seconds%60}", 470, 270, align-TextAlign.CENTER, font="fontlrg")
        else:
            screen.blit("survived_for_seconds", (0,0))
            draw_text(f"{seconds}", 300, 310, align=TextAlign.RIGHT, font="fontlrg")

        if game.timer > high_score:
            anim_frame = (total_frames // 5) % 8
            screen.blit(f"newrecord{anim_frame}", (WIDTH // 2 - 575 // 2, 380))

def play_music(name, volume=0.3):
    try:
        music.play(name)
        music.set_volume(volume)
    #except Exception:
        #pass
    except Exception as e:    ###
        print(e)         ###

try:
    pygame.mixer.quit()
    pygame.mixer.init(48000, -16, 2, 1024)
    play_music("title_theme")
#except Exception:
    #pass
except Exception as e:    ###
    print(e)         ###

tileset_images = {}
keyboard_controls = KeyboardControls()
all_replays, high_score = load_replays()

state = State.TITLE
game = None

game_over_timer = 0
total_frames = 0

run()
