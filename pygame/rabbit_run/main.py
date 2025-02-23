import sys
import pygame
from random import random, randint, choice
from enum import Enum
from engine import keyboard, Actor, sounds

if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

engine = sys.modules["engine"]
engine_version = [int(s) if s.isnumeric() else s
                  for s in engine.__version__.split('.')]

if engine_version < [0,3]:
    print(f"This game requires at least version 0.3 of the engine. "
          f"You are using version {engine.__version__}. Please upgrade.")
    sys.exit()

WIDTH = 480
HEIGHT = 800
TITLE = "Run Rabbit Run"

ROW_HEIGHT = 40
DEBUG_SHOW_ROW_BOUNDARIES = True                #---------- temp

# this should come from the engine
class keys:
    SPACE = "space"
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"

class MyActor(Actor):
    def __init__(self, image, pos, anchor=("center","bottom")):
        super().__init__(image, pos, anchor)
        self.children = []

    def draw(self, offset_x, offset_y):
        self.x += offset_x
        self.y += offset_y

        super().draw()
        for child_obj in self.children:
            child_obj.draw(self.x, self.y)

        self.x -= offset_x
        self.y -= offset_y

    def update(self):
        for child_obj in self.children:
            child_obj.update()

class Eagle(MyActor):
    def __init__(self, pos):
        super().__init__("eagles", pos)
        self.children.append(MyActor("eagle", (0, -32)))

    def update(self):
        self.y += 12

class PlayerState(Enum):
    ALIVE = 0,
    SPLAT = 1,
    SPLASH = 2,
    EAGLE = 3

DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

direction_keys = [keys.UP, keys.RIGHT, keys.DOWN, keys.LEFT]

DX = [0, 4, 0, -4]
DY = [-4, 0, 4, 0]

class Rabbit(MyActor):
    MOVE_DISTANCE = 10

    def __init__(self, pos):
        super().__init__("blank", pos)
        self.state = PlayerState.ALIVE
        self.direction = 2
        self.timer = 0
        self.input_queue = []
        self.min_y = self.y

    def handle_input(self, direction):
        for row in game.rows:
            if row.y == self.y + Rabbit.MOVE_DISTANCE * DY[direction]:
                self.direction = direction
                self.timer = Rabbit.MOVE_DISTANCE
                game.play_sound("jump", 1)
                return

    def update(self):
        for direction in range(4):
            if key_just_pressed(direction_keys[direction]):
                self.input_queue.append(direction)

        if self.state == PlayerState.ALIVE:
            if self.timer == 0 and len(self.input_queue) > 0:
                self.handle_input(self.input_queue.pop(0))

            land = False

            if self.timer > 0:
                self.x += DX[self.direction]
                self.y += DY[self.direction]
                self.timer -= 1
                land = self.timer == 0

            current_row = None
            for row in game.rows:
                if row.y == self.y:
                    current_row = row
                    break

            if current_row:
                self.state, dead_obj_y_offset = current_row.check_collision(self.x)

                if self.state == PlayerState.ALIVE: 
                    self.x += current_row.push() 
                    if land:
                        current_row.play_sound()
                else:
                    if self.state == PlayerState.SPLAT:
                        current_row.children.insert(0, MyActor("splat" + \
                                str(self.direction), (self.x, dead_obj_y_offset)))
                    self.timer = 100
            else:
                if self.y > game.scroll_pos + HEIGHT + 80:
                    game.eagle = Eagle((self.x, game.scroll_pos))
                    self.state = PlayerState.EAGLE
                    self.timer = 150
                    game.play_sound("eagle")

            self.x = max(16, min(WIDTH -16, self.x))

        else:
            self.timer -= 1
            self.min_y = min(self.min_y, self.y)
            self.image = "blank"

            if self.state == PlayerState.ALIVE:
                if self.timer > 0:
                    self.image = "jump" + str(self.direction)
                else:
                    self.image = "sit" + str(self.direction)
            elif self.state == PlayerState.SPLASH and self.timer > 84:
                self.image = "splash" + str(int((100 - self.timer) / 2))

class Mover(MyActor):
    def __init__(self, dx, image, pos):
        super().__init__(image, pos)
        self.dx = dx

    def update(self):
        self.x += self.dx

class Car(Mover):
    SOUND_ZOOM = 0
    SOUND_HONK = 1
    
    def __init__(self, dx, pos):
        image = "car" + str(randint(0,3)) + ("0" if dx < 0 else "1")
        super().__init__(dx, image, pos)
        self.played = [False, False]
        self.sounds = [("zoom", 6), ("honk", 4)]

    def play_sound(self, num):
        if not self.played[num]:
            game.play_sound(*self.sounds[num])
            self.played[num] = True

class Log(Mover):
    def __init__(self, dx, pos):
        image = "log" + str(randint(0,1))
        super().__init__(dx, image, pos)

class Train(Mover):
    def __init__(self, dx, pos):
        image = "train" + str(randint(0,2)) + ("0" if dx < 0 else "1")
        super().__init__(dx, image, pos)

class Row(MyActor):
    def __init__(self, base_image, index, y):
        super().__init__(base_image + str(index), (0,y), ("left","bottom"))
        self.index = index
        self.dx = 0

    def next(self):
        return

    def collide(self, x, margin=0):
        for child_obj in self.children:
            if x >= child_obj.x - (child_obj.width / 2) - margin \
                    and x < child_obj.x + (child_obj.width / 2) + margin:
                        return child_obj
        return None

    def push(self):
        return 0

    def check_collision(self, x):
        return PlayerState.ALIVE, 0

    def allow_movement(self, x):
        return x >= 16 and x <= WIDTH - 16

class ActiveRow(Row):
    def __init__(self, child_type, dxs, base_image, index, y):
        super().__init__(base_image, index, y)
        self.child_type = child_type
        self.timer = 0
        self.dx = choice(dxs)

        x = -WIDTH / 2 - 70
        while x < WIDTH / 2 + 70:
            x += randint(240,480)
            pos = (WIDTH / 2 + (x if self.dx > 0 else -x), 0)
            self.children.append(self.child_type(self.dx, pos))

    def update(self):
        super().update()
        self.children = [c for c in self.children if c.x > -70 and c.x < WIDTH + 70]
        self.timer -= 1

        if self.timer < 0:
            pos = (WIDTH + 70 if self.dx < 0 else -70, 0)
            self.children.append(self.child_type(self.dx, pos))
            self.timer = (1.0 + random()) * (240.0 / abs(self.dx))

class Hedge(MyActor):
    def __init__(self, x, y, pos):
        super().__init__("bush"+str(x)+str(y), pos)

def generate_hedge_mask():
    mask = [random() < 0.01 for i in range(12)]
    mask[randint(0,11)] = True
    mask = [sum(mask[max(0, i-1):min(12, i+ 2)]) > 0 for i in range(12)]
    return [mask[0]] + mask + 2 * [mask[-1]]

def classify_hedge_segment(mask, previous_mid_segment):
    if mask[1]:
        sprite_x = None
    else:
        sprite_x = 3 - 2 * mask[0] - mask[2]

    if sprite_x == 3:
        if previous_mid_segment == 4 and mask[3]:
            return 5, None
        else:
            if previous_mid_segment == None or previous_mid_segment == 4:
                sprite_x = 3
            elif previous_mid_segment == 3:
                sprite_x = 4
            return sprite_x, sprite_x
    else:
        return sprite_x, None

class Grass(Row):
    def __init__(self, predecessor, index, y):
        super().__init__("grass", index, y)
        self.hedge_row_index = None
        self.hedge_mask = None
                         
        if not isinstance(predecessor, Grass) or predecessor.hedge_row_index == None:
            if random() < 0.5 and index > 7 and index < 14:
                self.hedge_mask = generate_hedge_mask()
                self.hedge_row_index = 0
        elif predecessor.hedge_row_index == None:
            self.hedge_mask = predecessor.hedge_mask
            self.hedge_row_index = 1
        
        if self.hedge_row_index != None:
            previous_mid_segment = None
            for i in range(1,13):
                sprite_x, previous_mid_segment = \
                        classify_hedge_segment(self.hedge_mask[i-1:i+3],
                                               previous_mid_segment)
                if sprite_x != None:
                    self.children.append(Hedge(sprite_x, self.hedge_row_index,
                                               (i * 40 - 20, 0)))

    def allow_movement(self, x):
        return super().allow_movement(x) and not self.collide(x, 8)

    def play_sound(self):
        game.play_sound("grass", 1)

    def next(self):
        if self.index <= 5:
            row_class, index = Grass, self.index + 8
        elif self.index == 6:
            row_class, index = Grass, 7
        elif self.index == 7:
            row_class, index = Grass, 15
        elif self.index >= 8 and self.index <= 14:
            row_class, index = Grass, self.index + 1
        else:
            row_class, index = choice((Road, Water)), 0

        return row_class(self, index, self.y - ROW_HEIGHT)

class Dirt(Row):
    def __init__(self, predecessor, index, y):
        super().__init__("dirt", index, y)

    def play_sound(self):
        game.play_sound("dirt", 1)

    def next(self):
        if self.index <= 5:
            row_class, index = Dirt, self.index + 8
        elif self.index == 6:
            row_class, index = Dirt, 7
        elif self.index == 7:
            row_class, index = Dirt, 15
        elif self.index >= 8 and self.index <= 14:
            row_class, index = Dirt, self.index + 1
        else:
            row_class, index = choice((Road, Water)), 0

        return row_class(self, index, self.y - ROW_HEIGHT)

class Water(ActiveRow):
    def __init__(self, predecessor, index, y):
        dxs = [-2,-1] * (predecessor.dx >= 0) + [1,2] * (predecessor.dx <= 0)
        super().__init__(Log, dxs, "water", index, y)

    def update(self):
        super().update()

        for log in self.children:
            if game.rabbit and self.y == game.rabbit.y \
                    and log == self.collide(game.rabbit.x, -4):
                        log.y = 2
            else:
                log.y = 0

    def push(self):
        return self.dx

    def check_collision(self, x):
        if self.collide(x, -4):
            return PlayerState.ALIVE, 0
        else:
            game.play_sound("splash")
            return PlayerState.SPLASH, 0

    def play_sound(self):
        game.play_sound("log", 1)

    def next(self):
        if self.index == 7 or (self.index >= 1 and random() < 0.5):
            row_class, index = Dirt, randint(4,6)
        else:
            row_class, index = Water, self.index + 1

        return row_class(self, index, self.y - ROW_HEIGHT)

class Road(ActiveRow):
    def __init__(self, predecessor, index, y):
        dxs = list(set(range(-5,6)) - set([0, predecessor.dx]))
        super().__init__(Car, dxs, "road", index, y)

    def update(self):
        super().update()

        for y_offset, car_sound_num in [(-ROW_HEIGHT, Car.SOUND_ZOOM),
                                        (0, Car.SOUND_HONK),
                                        (ROW_HEIGHT, Car.SOUND_ZOOM)]:
            if game.rabbit and game.rabbit.y == self.y + y_offset:
                for child_obj in self.children:
                    if isinstance(child_obj, Car):
                        dx = child_obj.x - game.rabbit.x
                        if abs(dx) < 100 and ((child_obj.dx < 0) != (dx < 0)) \
                                and (y_offset == 0 or abs(child_obj.dx) > 1):
                                    child_obj.play_sound(car_sound_num)

    def check_collision(self, x):
        if self.collide(x):
            game.play_sound("splat", 1)
            return PlayerState.SPLAT, 0
        else:
            return PlayerState.ALIVE, 0

    def play_sound(self):
        game.play_sound("road", 1)

    def next(self):
        if self.index == 0:
            row_class, index = Road, 1
        elif self.index < 5:
            r = random()
            if r < 0.8:
                row_class, index = Road, self.index + 1
            elif r > 0.88:
                row_class, index = Grass, randint(0,6)
            elif r > 0.94:
                row_class, index = Rail, 0
            else:
                row_class, index = Pavement, 0
        else:
            r = random()
            if r < 0.6:
                row_class, index = Grass, randint(0,6)
            elif r > 0.9:
                row_class, index = Rail, 0
            else:
                row_class, index = Pavement, 0

        return row_class(self, index, self.y - ROW_HEIGHT)

class Pavement(Row):
    def __init__(self, predecessor, index, y):
        super().__init__("side", index, y)

    def play_sound(self):
        game.play_sound("sidewalk", 1)

    def next(self):
        if self.index < 2:
            row_class, index = Pavement, self.index + 1
        else:
            row_class, index = Road, 0

        return row_class(self, index, self.y - ROW_HEIGHT)

class Rail(Row):
    def __init__(self, predecessor, index, y):
        super().__init__("rail", index, y)
        self.predecessor = predecessor

    def update(self):
        super().update()

        if self.index == 1:
            self.children = [c for c in self.children if c.x > -1000
                             and c.x < WIDTH + 1000]

            if self.y < game.scroll_pos+HEIGHT and len(self.children) == 0 and random() < 0.01:
                dx = choice([-20, 20])
                self.children.append(Train(dx, (WIDTH + 1000 if dx < 0 else -1000, -13)))
                game.play_sound("bell")
                game.play_sound("train", 2)

    def check_collision(self, x):
        if self.index == 2 and self.predecessor.collide(x):
            game.play_sound("splat", 1)
            return PlayerState.SPLAT, 8
        else:
            return PlayerState.ALIVE, 0

    def play_sound(self):
        game.play_sound("grass", 1)

    def next(self):
        if self.index < 3:
            row_class, index = Rail, self.index + 1
        else:
            item = choice( ((Road, 0), (Water, 0)) )
            row_class, index = item[0], item[1]

        return row_class(self, index, self.y - ROW_HEIGHT)

class Game:
    def __init__(self, rabbit=None):
        self.rabbit = rabbit
        self.looped_sounds = {}

        try:
            if rabbit:
                music.set_volume(0.4)
            else:
                music.play("theme")
                music.set_volume(1)
        except:
            pass

        self.eagle = None
        self.frame = 0
        self.rows = [Grass(None, 0, 0)]
        self.scroll_pos = -HEIGHT

    def update(self):
        if self.rabbit:
            self.scroll_pos -= max(1, min(3, float(self.scroll_pos + HEIGHT -
                                                   self.rabbit.y) / (HEIGHT // 4)))
        else:
            self.scroll_pos -= 1

        self.rows = [row for row in self.rows if row.y < int(self.scroll_pos) +
                     HEIGHT + ROW_HEIGHT * 2]

        while self.rows[-1].y > int(self.scroll_pos) + ROW_HEIGHT:
            new_row = self.rows[-1].next()
            self.rows.append(new_row)

        for obj in self.rows + [self.rabbit, self.eagle]:
            if obj:
                obj.update()

        if self.rabbit:
            for name, count, row_class in [("river", 2, Water), ("traffic", 3, Road)]:
                volume = sum([16.0 / max(16.0, abs(r.y - self.rabbit.y)) for r in 
                              self.rows if isinstance(r, row_class)]) - 0.2
                volume = min(0.4, volume)
                self.loop_sound(name, count, volume)

        return self

    def draw(self):
        all_objs = list(self.rows)

        if self.rabbit:
            all_objs.append(self.rabbit)

        def sort_key(obj):
            return (obj.y + 39) // ROW_HEIGHT

        all_objs.sort(key=sort_key)
        all_objs.append(self.eagle)

        for obj in all_objs:
            if obj:
                obj.draw(0, -int(self.scroll_pos))

        if DEBUG_SHOW_ROW_BOUNDARIES:
            for obj in all_objs:
                if obj and isinstance(obj, Row):
                    # TO_DO: temporarily setting to black, since screen is white at this point in development
                    pygame.draw.rect(screen.surface, (0,0,0),
                                     pygame.Rect(obj.x, obj.y - int(self.scroll_pos),
                                                 screen.surface.get_width(), ROW_HEIGHT), 1)
                    # engine implements this as draw_text, not draw.text
                    screen.draw_text(str(obj.index), (obj.x, obj.y -
                                                      int(self.scroll_pos) - ROW_HEIGHT))

    def score(self):
        return int(-320 - game.rabbit.min_y) // 40

    def play_sound(self, name, count=1):
        if self.rabbit:
            sound = getattr(sounds, name + str(randint(0, count - 1)))
            sound.play()

    def loop_sound(self, name, count, volume):
        if volume > 0 and not name in self.looped_sounds:
            full_name = name + str(randint(0, count-1))
            sound = getattr(sounds, full_name)
            sound.play(-1)
            self.looped_sounds[name] = sound

        if name in self.looped_sounds:
            sound = self.looped_sounds[name]
            if volume > 0:
                sound.set_volume(volume)
            else:
                sound.stop()
                del self.looped_sounds[name]

    def stop_looped_sounds(self):
        for sound in self.looped_sounds.values():
            sound.stop()
        self.looped_sounds.clear()

key_status = {}

def key_just_pressed(key):
    result = False
    prev_status = key_status.get(key, False)

    if not prev_status and keyboard[key]:
        result = True

    key_status[key] = keyboard[key]

    return result

def display_number(n, color, x, align):
    n = str(n)
    for i in range(len(n)):
        screen.blit("digit" + str(color) + n[i], (x + (i - len(n) * align) * 25, 0))

class State(Enum):
    MENU = 1,
    PLAY = 2,
    GAME_OVER = 3

def update():
    global state, game, high_score

    if state == State.MENU:
        if key_just_pressed(keys.SPACE):
            state = State.PLAY
            game = Game(Rabbit((240, -320)))
        else:
            game.update()

    elif state == State.PLAY:
        if game.rabbit.state != PlayerState.ALIVE and game.rabbit.timer < 0:
            high_score = max(high_score, game.score())

            try:
                with open("high.txt", "w") as file:
                    file.write(str(high_score))
            except:
                pass

            state = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if key_just_pressed(keys.SPACE):
            game.stop_looped_sounds()
            state = State.MENU
            game = Game()

def draw():
    game.draw()

    if state == State.MENU:
        screen.blit('title', (0,0))
        screen.blit('start' + str([0,1,2,1][game.scroll_pos // 6 % 4]),
                    ((WIDTH - 270) // 2, HEIGHT - 240))

    elif state == State.PLAY:
        display_number(game.score(), 0, 0, 0)
        display_number(high_score, 1, WIDTH - 10, 1)

    elif state == State.GAME_OVER:
        screen.blit("gameover", (0,0))

try:
    with open("high.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

state = State.MENU
game = Game()

#-----------------------
from engine import run
run()
