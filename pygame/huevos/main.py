import os
import sys
from enum import Enum
from random import randint
import pygame
from pygame import Rect
from engine import *

WIDTH = 480       ###
HEIGHT = 480      ###
TITLE = "Huevos"

MAX_REPLAYS = 1   ###
REPLAY_FILENAME = 'replays'
INITIAL_TIME_REMAINING = 0 ###
INITIAL_PICKUP_TIME_BONUS = 0 ###
INITIAL_LEVEL_CYCLE = 1 ###
LEVEL_SEQUENCE = [1] ###
GRID_BLOCK_SIZE = 32  ###

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

    def button_down(self, button):
        if button == 0:
            return keyboard.space
        else:
            return keyboard.z

    def button_pressed(self, button):
        return self.is_pressed[button]

class Gem:      ###
    def new_game():
        pass           ###

class Player:        ###
    def __init__(self, a):   ###
        self.replay_data = [(0,0),0,0]    ###
        pass          ###
    def draw(self):
        pass    ###
    def new_player(self,a):   ###
        pass    ###
    def reset(self):   ###
        pass    ###

class GhostPlayer:    ###
    def __init__(self, a):   ###
        pass    ###
    def draw(self):
        pass    ###

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
            self.player.new_player(player_start_pos)

        self.generate_block_rects()

        if self.player:
            self.player.reset()

        self.play_sound("new_wave")

    def load_level(self, a):   ###
        self.background_image = images.controls   ###
        self.tileset_image = images.controls   ###
        self.grid = [[0]]   ###
        self.collision_tiles = [1,2,3]  ###

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

keyboard_controls = KeyboardControls()
all_replays, high_score = load_replays()

state = State.TITLE
total_frames = 0

run()
