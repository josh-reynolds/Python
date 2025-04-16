from enum import Enum
from random import choice, randint
import pygame
from pygame import Rect
from pygame.math import Vector2
from engine import *

WIDTH = 800
HEIGHT = 480
TITLE = "Thud!"

MIN_WALK_Y = 1 ###

INTRO_ENABLED = False   ###

BACKGROUND_TILE_SPACING = 10 ###
BACKGROUND_TILES = [] ###

HEALTH_STAMINA_BAR_WIDTH = 5 ###

ANCHOR_CENTER = ('center', 'center')

ENEMY_APPROACH_PLAYER_DISTANCE_SCOOTERBOY = 1 ###

STAGES = []  ###

SPECIAL_FONT_SYMBOLS = {'xb_a' : '%'}
SPECIAL_FONT_SYMBOLS_INVERSE = dict((v,k) for k,v in SPECIAL_FONT_SYMBOLS.items())

fullscreen_black_bmp = pygame.Surface((0,0))  ###

class KeyboardControls:
    NUM_BUTTONS = 4

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
            return keyboard.space or keyboard.z or keyboard.lctrl   # punch
        elif button == 1:
            return keyboard.x or keyboard.lalt   # kick
        elif button == 2:
            return keyboard.c or keyboard.lshift  # elbow
        elif button == 3:
            return keyboard.a   # flying kick

    def button_pressed(self, button):
        return self.is_pressed[button]

class ScrollHeightActor: ###
    def __init__(self, a, b, anchor, separate_shadow):  ###
        pass   ###
class Player:  ###
    def __init__(self, a): ###
        self.lives = 1 ###
        self.health = 5 ###
        self.start_health = 5 ###
        self.stamina = 5 ###
        self.max_stamina = 5 ###
        self.vpos = Vector2(0,0)  ###
        self.extra_life_timer = 1  ###
        self.controls = a   ###
    def get_draw_order_offset(self):
        return 0 ###
    def update(self):
        pass ###
    def draw(self, a): ###
        pass ###
class Enemy:
    class State(Enum):
        RIDING_SCOOTER = 1 ###
    def __init__(self, a, b, c, color_variant, score, start_timer, speed=1, health=1, stamina=1,
                 anchor_y=1, half_hit_area=1, approach_player_distance=1):  ###
        pass  ###

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

class EnemyScooterboy(Enemy):
    SCOOTER_SPEED_SLOW = 4

    def __init__(self, pos, start_timer=20):
        attacks = ("scooterboy_attack1")
        super().__init__(pos, "scooterboy", attacks, start_timer=start_timer,
                         approach_player_distance=ENEMY_APPROACH_PLAYER_DISTANCE_SCOOTERBOY,
                         color_variant=randint(0,2), score=30)
        self.state = Enemy.State.RIDING_SCOOTER
        self.scooter_speed = EnemyScooterboy.SCOOTER_SPEED_SLOW
        self.scooter_target_speed = self.scooter_speed
        self.scooter_sound_channel = None

class EnemyBoss(Enemy):
    def __init__(self, pos, start_timer=20):
        boss_attacks = ("boss_lpunch", "boss_rpunch", "boss_kick", "boss_grab_player",)
        super().__init__(pos, "boss", boss_attacks, speed=Vector2(0.9,0.8), health=25,
                         stamina=1000, start_timer=start_timer, anchor_y=280,
                         half_hit_area=Vector2(30,20), color_variant=randint(0,2),
                         score=75)

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

class Barrel(Weapon):
    def __init__(self, pos):
        super().__init__("barrel", "barrel_upright", pos, end_pickup_frame=2,
                         anchor=("center",190), bounciness=0.75, ground_friction=0.96,
                         separate_shadow=True)
        self.last_thrower = None
        self.frame = 0

class Stage:
    def __init__(self, enemies, max_scroll_x, weapons=[], powerups=[]):
        self.enemies = enemies
        self.powerups = powerups
        self.max_scroll_x = max_scroll_x
        self.weapons = weapons

def setup_stages():
    global STAGES
    STAGES = (
            Stage(max_scroll_x=300, enemies=[EnemyVax(pos=(1000,400))]),
            Stage(max_scroll_x=600,
                  enemies=[EnemyVax(pos=(1400,400)), EnemyHoodie(pos=(1500,500))],
                  weapons=[Barrel((1600,400))]),
            Stage(max_scroll_x=600, enemies=[EnemyScooterboy(pos=(200,400))]),
            Stage(max_scroll_x=900,
                  enemies=[EnemyBoss(pos=(1800,400)), EnemyVax(pos=(400,40))]),
            # more stages on GitHub
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

    def update(self):
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
                self.scrolling = Falsee
        else:
            begin_scroll_boundary = WIDTH - 300
            if self.player.vpos.x - self.scroll_offset.x > begin_scroll_boundary \
                    and self.scroll_offset.x < self.max_scroll_offset_x:
                        self.scrolling = True
                        if self.stage_index < len(STAGES):
                            stage = STAGE[self.stage_index]
                            self.create_stage_objects(stage)

        self.score += sum([enemy.score for enemy in self.enemies if enemy.lives <= 0])
        self.enemies = [enemy for enemy in self.enemies if enemy.lives > 0]
        self.scooters = [scooter for scooter in self.scooters if scooter.frame < 200]
        self.weapons = [weapon for weapon in self.weapons if not weapon.is_broken() and weapon.x > -200]
        self.powerups = [powerup for powerup in self.powerups if not powerup.collected and powerup.x > -200]

        if len(self.enemies) == 0 and self.scroll_offset.x == self.max_scroll_offset_x:
            self.next_stage()

    def draw(self):
        self.draw_background()

        all_objs = [self.player] + self.enemies + self.weapons + self.scooters + self.powerups
        all_objs.sort(key=lambda obj: obj.vpos.y + obj.get_draw_order_offset())
        for obj in all_objs:
            if obj:
                obj.draw(self.scroll_offset)

        if self.scroll_offset.x < self.max_scroll_offset_x and (self.timer//30) % 2 == 0:
            screen.blit("arrow", (WIDTH-450,120))

        self.draw_ui()

        if self.text_active or self.timer < 255:
            if self.text_active:
                alpha = 255
            else:
                alpha = max(0, 255 - self.timer)
            fullscreen_black_bmp.set_alpha(alpha)
            screen.blit(fullscreen_black_bmp, (0, 0))

        if self.text_active:
            draw_text(self.displayed_text, 50, 50)

    def draw_ui(self):
        full_w = HEALTH_STAMINA_BAR_WIDTH
        health_w = int((game.player.health / game.player.start_health) * full_w)
        screen.surface.blit(getattr(images,"health"), (48,11), Rect(0,0,health_w,full_w))

        stam_w = int((game.player.stamina / game.player.max_stamina) * full_w)
        screen.surface.blit(getattr(images,"stamina"), (517,11), Rect(0,0,stam_w,full_w))

        screen.blit("status", (0,0))

        for i in range(game.player.lives):
            if game.player.extra_life_timer <= 0 or i < game.player.lives - 1:
                sprite_idx = 9
            else:
                sprite_idx = min(9, (30 - game.player.extra_life_timer) // 3)
            screen.blit("status_life" + str(sprite_idx), (i * 46 - 55, -35))

        draw_text(f"{self.score:04}", WIDTH // 2, 0, True)

    def draw_background(self):
        road1_x = -(self.scroll_offset.x % WIDTH)
        road2_x = road1_x + WIDTH
        screen.blit("road",(road1_x, 0))
        screen.blit("road",(road2_x, 0))

        pos = -self.scroll_offset
        pos.x -= BACKGROUND_TILE_SPACING

        for tile in BACKGROUND_TILES:
            if pos.x + 417 >= 0:
                screen.blit(tile, pos)
                pos.x += BACKGROUND_TILE_SPACING
                if pos.x >= WIDTH:
                    break
            else:
                pos.x += BACKGROUND_TILE_SPACING

    def shutdown(self):
        for enemy in self.enemies:
            enemy.died()

    def play_sound(self, name, count=1):
        if self.player:
            return getattr(sounds, name + str(randint(0, count - 1)))

def get_char_image_and_width(char):
    if char == " ":
        return None, 22
    else:
        if char in SPECIAL_FONT_SYMBOLS_INVERSE:
            image= getattr(images, SPECIAL_FONT_SYMBOLS_INVERSE[char])
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

class State(Enum):
    TITLE = 1
    CONTROLS = 2
    PLAY = 3
    GAME_OVER = 4

def update():
    global state, game, total_frames

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

total_frames = 0

keyboard_controls = KeyboardControls()

state = State.TITLE

run()
