import math
from enum import Enum, IntEnum
from random import randint, uniform
import pygame
from pygame.math import Vector2
from engine import *

WIDTH = 960
HEIGHT = 540
TITLE = "Invader"

LEVEL_WIDTH = 500               ###
LEVEL_HEIGHT = 500               ###
TERRAIN_OFFSET_Y = 5               ###
WAVE_COMPLETE_SCREEN_DURATION = 20    ###
HUMAN_START_POS = [(1,2),(1,2)]             ###

class Mock:                    ###
    def draw(self):               ###
        pass                     ###

def sign(a):    ###
    return 1      ###

def forward_backward_animation_frame(a,b):   ###
    return 0                 ###

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

    def get_x(self):           ###
        return 1                   ###
    def get_y(self):           ###
        return 1                   ###

class WrapActor(Actor):
    def __init__(self, image, pos):
        super().__init__(image, pos)

    def update(self):      
        pass             ###
    def draw(self, a, b):    ###
        pass                ###

class Laser:       ###
    def __init__(self, a, b, c):    ###
        pass           ###
    def update(self):      
        pass             ###
    def draw(self, a, b):    ###
        pass                ###

class Player(WrapActor):
    EXPLODE_FRAMES = 1    ###
    EXPLODE_ANIM_SPEED = 2     ###
    DRAG = Vector2(1,1)             ###
    FORCE = Vector2(1,1)             ###

    def __init__(self, controls):
        super().__init__("blank", (WIDTH / 2, LEVEL_HEIGHT / 2))

        self.controls = controls

        self.velocity = Vector2(0,0)
        self.lives = 5
        self.shields = 5
        self.extra_life_tokens = 0
        self.facing_x = 1
        self.tilt_y = 0
        self.timers = [0, 0, 0, 0]
        self.frame = 0
        self.carried_human = None
        self.blip = Actor("dot-white")
        self.thrust_sprite = WrapActor("blank", (0,0))

        try:
            self.thrust_sound = sounds.thrust0
        except Exception:
            self.thrust_sound = None
        self.thrust_sound_playing = False

    class Timer(IntEnum):
        FIRE = 1,            ###
        EXPLODE = 2,            ###
        HURT = 3,            ###

    def update(self):      
        self.timers = [i - 1 for i in self.timers]

        if self.timers[Player.Timer.EXPLODE] > 0:
            frame = (Player.EXPLODE_FRAMES - self.timers[Player.Timer.EXPLODE]) // Player.EXPLODE_ANIM_SPEED
            self.image = "ship_explode" + str(frame)
            self.thrust_sprite.image = "blank"

            if self.timers[Player.Timer.EXPLODE] == 1 and self.lives > 0:
                self.respawn()

        elif self.lives == 0:
            self.image = "blank"
            self.thrust_sprite.image = "blank"

        else:
            x_input = self.controls.get_x()
            y_input = self.controls.get_y()

            move = Vector2(x_input, y_input)
            self.tilt_y = y_input

            if x_input != 0:
                self.facing_x = sign(x_input)

            if self.frame % 8 != 0 or sign(self.facing_x) != sign(move.x):
                move.x = 0

            self.velocity = Vector2(self.velocity.x * Player.DRAG.x + move.x * Player.FORCE.x,
                                    self.velocity.y * Player.DRAG.y + move.y * Player.FORCE.y)

            self.pos += self.velocity

            self.y = max(0, min(LEVEL_HEIGHT, self.y))

            self.blip.pos = game.radar.radar_pos(self.pos)

            if self.carried_human is None:
                for human in game.humans:
                    if human.can_be_picked_up_by_player() \
                            and (Vector2(human.pos) - self.pos).length() < 40:
                                human.picked_up(self)
                                self.carried_human = human
                                break
            else:
                self.carried_human.pos = (self.pos[0], self.pos[1] + 50)
                if self.carried_human.terrain_check():
                    self.carried_human.dropped()
                    self.carried_human = None
                    game.play_sound("rescue_prisoner")

            target = 8 if self.facing_x < 0 else 0

            if self.frame == target:
                if self.controls.button_down(0) and self.timers[Player.Timer.FIRE] <= 0:
                    self.timers[Player.Timer.FIRE] = 10
                    laser_vel_x = self.velocity[0] + 20 * self.facing_x
                    laser_x = self.x + 40 * self.facing_x
                    laser_y = self.y + self.get_laser_fire_y_offset()
                    game.lasers.append(Laser(laser_x, laser_y, laser_vel_x))
            else:
                if self.timers[Player.Timer.ANIM] <= 0:
                    self.timers[Player.Timer.ANIM] = 3
                    self.frame = (self.frame + 1) % 16

            try:
                if self.thrust_sound is not None:
                    if move.x != 0 and self.frame == target and not self.thrust_sound_playing:
                        self.thrust_sound.set_volume(0.3)
                        self.thrust_sound.play(loops=-1, fade_ms=200)
                        self.thrust_sound_playing = True
                    elif (move.x == 0 or self.frame != target) and self.thrust_sound_playing:
                        self.thrust_sound.fadeout(200)
                        self.thrust_sound_playing = False
            #except Exception:
                #pass
            except Exception as e:             ###
                print(e)                    ###

            anim_type = "ship" if self.timers[Player.Timer.HURT] <= 0 else "hurt"
            tilt = ""
            if self.frame % 8 == 0 and self.tilt_y != 0:
                tilt = "u" if self.tilt_y < 0 else "d"
            self.image = anim_type + str(self.frame) + tilt

            if self.frame % 8 != 0 or move.x == 0:
                self.thrust_sprite.image = "blank"
            else:
                direction = 0 if move.x > 0 else 1
                frame = (game.timer // 3) % 2
                self.thrust_sprite.image = f"boost_{direction}_{frame}"
                x_offset = 66
                y_offset = -3
                self.thrust_sprite.pos = (self.x + x_offset * -move.x,
                                          self.y + y_offset)

    def flash(self, offset_x, offset_y):
        if self.frame % 8 == 0 and self.timers[Player.Timer.FIRE] > 5:
            sprite = "flash" + str(self.frame // 8)
            x = self.x + offset_x - 25
            y = self.y + offset_y -13 + self.get_laser_fire_y_offset()
            screen.blit(sprite, (x,y))

    def get_laser_fire_y_offset(self):
        return 1                        ###

    def draw(self, offset_x, offset_y):
        if self.tilt_y == 1:
            self.flash(offset_x, offset_y)

        super().draw(offset_x, offset_y)

        self.thrust_sprite.draw(offset_x, offset_y)

        if self.tilt_y != 1:
            self.flash(offset_x, offset_y)

    def is_carrying_human(self):
        return self.carried_human is not None

    def level_ended(self, shield_restore_amount, humans_saved):
        self.shields = min(self.shields + shield_restore_amount, 5)
        if humans_saved == 10:
            self.extra_life_tokens += 1
            if self.extra_life_tokens >= 3:
                self.lives += 1
                self.extra_life_tokens -= 3

class Radar(Actor):
    def __init__(self):
        super().__init__("radar", pos=(WIDTH/2, 4), anchor=('center', 'top'))

    def radar_pos(self, pos):
        return (self.left + ((int(pos[0]) % LEVEL_WIDTH) / 11.5),
                self.y + (int(pos[1]) // 11))

class EnemyState(Enum):
    START = 0,
    ALIVE = 1,
    EXPLODING = 2,
    DEAD = 3

class EnemyType(Enum):
    LANDER = 0,
    MUTANT = 1,
    BAITER = 2,
    POD = 3,
    SWARMER = 4

class Enemy(WrapActor):
    def __init__(self, start_timer=0, type=EnemyType.LANDER, pos=None, start_vel=None):
        if pos is None:
            pos = (randint(0, LEVEL_WIDTH - 1), randint(32, LEVEL_HEIGHT - 32))

        super().__init__("blank", pos)

        self.type = type

        if self.type == EnemyType.LANDER:
            self.max_speed = 5
            self.acceleration = 0.1
        elif self.type == EnemyType.MUTANT:
            self.max_speed = 9
            self.acceleration = 0.5
        elif self.type == EnemyType.BAITER:
            self.max_speed = 9
            self.acceleration = 0.01
        elif self.type == EnemyType.POD:
            self.max_speed = 10
            self.acceleration = 0.03
        elif self.type == EnemyType.SWARMER:
            self.max_speed = 8
            self.acceleration = 1

        self.target_pos = Vector2(self.x+uniform(-100,100), self.y+uniform(-100,100))
        self.update_target_timer = 0

        self.velocity = start_vel if start_vel is not None else Vector2(0,0)

        if self.type == EnemyType.SWARMER:
            self.state = EnemyState.ALIVE
            self.state_timer = 0
        else:
            self.state = EnemyState.START
            self.state_timer = start_timer

        self.target_human = None
        self.carrying = False
        self.bullet_timer = randint(30, 90)
        self.fire_angle = 0
        self.blip = Actor("dot-red")
        self.anim_timer = randint(0, 47)

    def update(self):      
        super().update()

        if self.state == EnemyState.START:
            self.state_timer+= 1
            if self.state_timer == 1:
                if self.type == EnemyType.MUTANT:
                    game.play_sound("enemy_appear_mutant")
                elif self.type == EnemyType.LANDER:
                    game.play_sound("enemy_appear_normal")
                elif self.type == EnemyType.BAITER:
                    game.play_sound("enemy_appear_ufo")

            if self.state_timer == 33:
                self.state = EnemyState.ALIVE
            elif self.state_timer >= 0:
                self.image = "appear" + str(self.state_timer // 3)

        elif self.state == EnemyState.ALIVE:
            max_speed = self.max_speed

            if self.target_human is not None and self.target_human.dead:
                self.target_human = None
                self.carrying = False

            if self.target_human is None and self.type == EnemyType.LANDER and uniform(0,1) < 0.001:
                target_humans = [enemy.target_human for enemy in game.enemies
                                 if enemy.target_human is not None]
                available_humans = [human for human in game.humans 
                                    if human not in target_humans
                                    and human.can_be_picked_up_by_enemy()]
                if len(available_humans) > 0:
                    dist = lambda human: (Vector2(human.pos) - self.pos).length_squared()
                    self.target_human = min(available_humans, key=dist)

            if self.target_human is not None:
                if self.carrying:
                    self.target_pos = Vector2(self.pos[0], 64)
                    max_speed = 0.5

                    if abs(self.pos[1] - self.target_pos.y) < 10:
                        game.enemies.append(Enemy(type=EnemyType.MUTANT,
                                                  pos=self.target_human.pos))
                        self.target_human.die()
                        self.target_human = None
                        self.carrying = False
                else:
                    x_distance = abs(self.x - self.target_human.x)
                    if x_distance < 80:
                        max_speed = 1
                    if x_distance > 100:
                        self.target_pos = Vector2(self.target_human.pos) - Vector2(0, 200)
                    else:
                        self.target_pos = Vector2(self.target_human.pos)
                        distance = Vector2(self.pos - self.target_pos).length()
                        if distance < 55:
                            self.carrying = True
                            self.target_human.picked_up(self)
            else:
                self.update_target_timer -= 1
                if self.update_target_timer <= 0:
                    self.update_target_timer = 60

                    player_pos = Vector2(game.player.pos)

                    max_player_distance = 500 if self.type == EnemyType.LANDER else LEVEL_WIDTH

                    if (self.pos - player_pos).length() < max_player_distance:
                        self.target_pos = player_pos

                    x_range = 800 if self.type == EnemyType.BAITER else 100
                    y_range = 300 if self.type == EnemyType.BAITER else 100
                    self.target_pos = self.target_pos + Vector2(uniform(-x_range, x_range),
                                                                uniform(-y_range, y_range))

                    distance = (self.target_pos - self.pos).length()
                    if distance > 0:
                        vec = (self.target_pos - self.pos).normalize()
                    else:
                        vec = Vector2(0,0)

                    force = vec * self.acceleration

                    if self.y < 64:
                        force.y += 0.2
                    if self.y > LEVEL_HEIGHT-64:
                        force.y -= 0.2

                    self.velocity += force

                    if self.velocity.length() > max_speed:
                        self.velocity.scale_to_length(max(self.velocity.length()*0.9, max_speed))

                    self.pos += self.velocity

                    if self.carrying:
                        self.target_human.pos = (self.pos[0], self.pos[1] + 50)

                    self.bullet_timer -= 1
                    if self.bullet_timer <= 0:
                        if self.type == EnemyType.BAITER:
                            velocity = Vector2(cos(self.fire_angle), sin(self.fire_angle)) * 3
                            game.bullets.append(Bullet(self.pos, velocity))
                            self.bullet_timer = 8
                            self.fire_angle += 0.3

                        elif game.player.lives > 0:
                            player_vec = Vector2(game.player.pos) - self.pos
                            player_distance = player_vec.length()
                            if 100 < player_distance < 300:
                                player_vec.normalize_ip()
                                velocity = Vector2(player_vec.x + uniform(-0.5, 0.5),
                                                   player_vec.y + uniform(-0.5, 0.5)) * 6
                                game.bullets.append(Bullet(self.pos, velocity))

                                upper_limit = 30 if self.type == EnemyType.MUTANT else 90
                                self.bullet_timer = randint(20, upper_limit)

                    if self.type == EnemyType.LANDER:
                        frame = 0
                        if self.target_human is not None:
                            if self.carrying:
                                frame = 2
                            else:
                                distance = (Vector2(self.pos) - self.target_human.pos).length()
                                if distance < 90:
                                    frame = 1
                        self.image = "lander" + str(frame)
                    elif self.type == EnemyType.MUTANT:
                        self.anim_timer += 1
                        self.image = "mutant" + str((self.anim_timer // 6) % 4)
                    elif self.type == EnemyType.BAITER:
                        self.anim_timer += 1
                        self.image = "baiter" + str((self.anim_timer // 3) % 8)
                    elif self.type == EnemyType.POD:
                        self.anim_timer += 1
                        frame = forward_backward_animation_frame(self.anim_timer // 6, 3)
                        if self.velocity.x > 0:
                            frame += 3
                        self.image = "pod" + str(frame)
                    elif self.type == EnemyType.SWARMER:
                        self.anim_timer += 1
                        self.image = "swarmer" + str((self.anim_timer // 6) % 8)

                elif self.state == EnemyState.EXPLODING:
                    self.anim_timer += 1
                    frame = self.anim_timer // 2
                    self.image = "enemy_explode" + str(min(9, frame))

                    if frame == 10:
                        self.state = EnemyState.DEAD

                self.blip.pos = game.radar.radar_pos(self.pos)

class Human(WrapActor):
    def __init__(self, pos):
        super().__init__("blank", pos)

        self.y_velocity = 0
        self.blip = Actor("dot-green")
        self.anim_timer = 0
        self.waving = False
        self.dead = False
        self.exploding = False
        self.carrier = None
        self.falling = False

    def update(self):      
        super().update()

        self.anim_timer += 1

        if self.exploding:
            frame = self.anim_timer // 2
            if frame >= 10:
                self.dead = True
            else:
                pos = self.pos
                self.anchor = (175,172)
                self.image = "human_explode" + str(frame)
                self.pos = pos
            return

        if self.carrier is None:
            self.falling = not self.terrain_check()
            if not self.falling and self.y_velocity > 1:
                self.die()

            if self.falling:
                self.y_velocity += 0.05
                self.y_velocity = min(self.y_velocity, 4)
                self.y += self.y_velocity

        self.blip.pos = game.radar.radar_pos(self.pos)

        frame = self.anim_timer // 7
        num_frames = 4
        if self.carrier == game.player:
            sprite = "saved"
            num_frames = 1
        elif self.carrier is not None:
            sprite = "abducted"
        elif self.falling:
            sprite = "fall"
            num_frames = 2
        elif self.waving:
            sprite = "wave"
            num_frames = 3
            if self.anim_timer > 100:
                self.waving = False
        else:
            sprite = "stand"
            num_frames = 1
            if randint(0, 200) == 0:
                self.waving = True
                self.anim_timer = 0

        self.image = f"human_{sprite}{forward_backward_animation_frame(frame, num_frames)}"

    def can_be_picked_up_by_player(self):
        return self.carrier is None and self.falling and not self.dead

    def can_be_picked_up_by_enemy(self):
        return self.carrier is None and not self.falling and not self.dead

    def terrain_check(self):
        pos_terrain = (int(self.x % LEVEL_WIDTH), int(self.y - TERRAIN_OFFSET_Y))
        mask_width, mask_height = game.terrain_mask.get_size()
        if 0 <= pos_terrain[0] < mask_width and 0 <= pos_terrain[1] < mask_height:
            return game.terrain_mask.get_at(pos_terrain)
        elif pos_terrain[1] >= mask_height:
            return True
        return False

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
