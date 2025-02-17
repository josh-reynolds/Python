import pygame
from random import random, randint, choice
from enum import Enum
from engine import keyboard, Actor


WIDTH = 800
HEIGHT = 480
TITLE = "Run Rabbit Run"

ROW_HEIGHT = 10

DEBUG_SHOW_ROW_BOUNDARIES = True

class keys:
    SPACE = "space"

class MyActor(Actor):
    def __init__(self, image, pos, anchor=("center","bottom")):
        super().__init__(image, pos, anchor)
        self.children = []

class Car():
    def __init__(self, a, b):
        pass

class Log():
    def __init__(self, a, b):
        pass

class Row(MyActor):
    def __init__(self, base_image, index, y):
        super().__init__(base_image + str(index), (0,y), ("left","bottom"))
        self.index = index
        self.dx = 0

    def update(self):
        pass

    def draw(self, a, b):
        pass

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

class Water(ActiveRow):
    def __init__(self, predecessor, index, y):
        dxs = [-2,-1] * (predecessor.dx >= 0) + [1,2] * (predecessor.dx <= 0)
        super().__init__(Log, dxs, "water", index, y)

    def next(self):
        i = min(self.index+1, 7)
        return Grass(self, i, self.y)

class Road(ActiveRow):
    def __init__(self, predecessor, index, y):
        dxs = list(set(range(-5,6)) - set([0, predecessor.dx]))
        super().__init__(Car, dxs, "road", index, y)

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

key_status = {}

def key_just_pressed(key):
    result = False
    prev_status = key_status.get(key, False)

    if not prev_status and keyboard[key]:
        result = True

    key_status[key] = keyboard[key]

    return result

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

state = State.MENU
game = Game()

#-----------------------
from engine import run
run()
