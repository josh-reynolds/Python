import pygame
from random import random, randint
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

class Row(MyActor):
    def __init__(self, base_image, index, y):
        super().__init__(base_image + str(index), (0,y), ("left","bottom"))
        self.index = 0

    def update(self):
        pass

    def draw(self, a, b):
        pass

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
