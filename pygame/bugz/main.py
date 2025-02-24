from enum import Enum
from random import random, randint
from engine import keyboard, Actor

WIDTH = 480    ###
HEIGHT = 800    ###
TITLE = "Bugz!"

DEBUG_TEST_RANDOM_POSITIONS = True    ###


num_grid_rows = 10    ###
num_grid_cols = 10    ###

def cell2pos(a, b, c, d):
    return [1,1,1,1]              ####

class FlyingEnemy:
    def __init__(self, a):
        self.health = 1     ###
        self.x = 1          ###

    def update(self):
        pass

    def draw(self):
        pass

class Explosion:
    pass

class Rock:
    def __init__(self, a, b):
        self.y = 1           ###

    def damage(self, a, b):
        pass

    def update(self):
        pass

    def draw(self):
        pass

SECONDARY_AXIS_POSITIONS = [x for x in range(16)]        ###
SECONDARY_AXIS_SPEED = [x for x in range(16)]        ###

DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]

def inverse_direction(direction):
    return 1                                  ###

def is_horizontal(direction):
    pass

class Segment(Actor):
    def __init__(self, cx, cy, health, fast, head):
        super().__init__("blank")
        self.cell_x = cx
        self.cell_y = cy
        self.health = health
        self.fast = fast
        self.head = head

        self.in_edge = DIRECTION_LEFT
        self.out_edge = DIRECTION_RIGHT

        self.disallow_direction = DIRECTION_UP
        self.previous_x_direction = 1

    def rank(self):
        def inner(a):                ###
            return 1                ###
        return inner                ###

    def update(self):
        phase = game.time % 16

        if phase == 0:
            self.cell_x += DX[self.out_edge]
            self.cell_y += DY[self.out_edge]
            self.in_edge = inverse_direction(self.out_edge)

            if self.cell_y == (18 if game.player else 0):
                self.disallow_direction = DIRECTION_UP
            if self.cell_y == num_grid_rows-1:
                self.disallow_direction = DIRECTION_DOWN
        elif phase == 4:
            self.out_edge = min(range(4), key=self.rank())

            if is_horizontal(self.out_edge):
                self.previous_x_direction = self.out_edge

            new_cell_x = self.cell_x + DX[self.out_edge]
            new_cell_y = self.cell_y + DY[self.out_edge]

            if new_cell_x >= 0 and new_cell_x < num_grid_cols:
                game.damage(new_cell_x, new_cell_y, 5)

            game.occupied.add((new_cell_x, new_cell_y))
            game.occupied.add((new_cell_x, new_cell_y, inverse_direction(self.out_edge)))

        turn_idx = (self.out_edge - self.in_edge) % 4

        offset_x = SECONDARY_AXIS_POSITIONS[phase] * (2 - turn_idx)
        stolen_y_movement = (turn_idx % 2) * SECONDARY_AXIS_POSITIONS[phase]
        offset_y = -16 + (phase * 2) - stolen_y_movement

        rotation_matrices = [[1,0,0,1],[0,-1,1,0],[-1,0,0,-1],[0,1,-1,0]]
        rotation_matrix = rotation_matrices[self.in_edge]
        offset_x, offset_y = offset_x * rotation_matrix[0] \
                           + offset_y * rotation_matrix[1], \
                             offset_x * rotation_matrix[2] \
                           + offset_y * rotation_matrix[3] \

        self.pos = cell2pos(self.cell_x, self.cell_y, offset_x, offset_y)

        direction = ((SECONDARY_AXIS_SPEED[phase] * (turn_idx - 2)) \
                  + (self.in_edge * 2) + 4) % 8

        leg_frame = phase // 4

        self.image = "seg" + str(int(self.fast)) + str(int(self.health == 2)) \
                   + str(int(self.head)) + str(direction) + str(leg_frame)

class Game:
    def __init__(self, player=None):
        self.wave = -1
        self.time = 0
        self.player = player
        self.grid = [[None] * num_grid_cols for y in range(num_grid_rows)]
        self.bullets = []
        self.explosions = []
        self.segments = []
        self.flying_enemy = None
        self.score = 0

    def damage(self, cell_x, cell_y, amount, from_bullet=False):
        rock = self.grid[cell_y][cell_x]

        if rock != None:
            if rock.damage(amount, from_bullet):
                self.grid[cell_y][cell_x] = None

        return rock != None

    def update(self):
        self.time += (2 if self.wave % 4 == 3 else 1)
        self.occupied = set()
        all_objects = sum(self.grid, self.bullets + self.segments +
                          self.explosions + [self.player] + [self.flying_enemy])

        for obj in all_objects:
            if obj:
                obj.update()

        self.bullets = [b for b in self.bullets if b.y > 0 and not b.done]
        self.explosions = [e for e in self.explosions if not e.timer == 31]
        self.segments = [s for s in self.segments if s.health > 0]

        if self.flying_enemy:
            if self.flying_enemy.health <= 0 or self.flying_enemy.x < -35 \
                    or self.flying_enemy.x > 515:
                        self.flying_enemy = None
        elif random() < 0.01:
            self.flying_enemy = FlyingEnemy(self.player.x if self.player else 240)

        if self.segments == []:
            num_rocks = 0
            for row in self.grid:
                for element in row:
                    if element != None:
                        num_rocks += 1
            if num_rocks < 31 + self.wave:
                while True:
                    x, y = randint(0, num_grid_cols-1), randint(1, num_grid_rows-1)
                    if self.grid[y][x] == None:
                        self.grid[y][x] = Rock(x, y)
                        break
            else:
                game.play_sound("wave")
                self.wave += 1
                self.time = 0
                self.segments = []
                num_segments = 8 + self.wave // 4 * 2
                for i in range(num_segments):
                    if DEBUG_TEST_RANDOM_POSITIONS:
                        cell_x, cell_y = randint(1, 7), randint(1, 7)
                    else:
                        cell_x, cell_y = -1-i, 0

                    health = [[1,1],[1,2],[2,2],[1.1]][self.wave % 4][i % 2]
                    fast = self.wave % 4 == 3
                    head = i == 0
                    self.segments.append(Segment(cell_x, cell_y, health, fast, head))

        return self

    def draw(self):
        screen.blit("bg" + str(max(self.wave, 0) % 3), (0,0))
        all_objs = sum(self.grid, self.bullets + self.segments + self.explosions + [self.player])

        def sort_key(obj):
            return (isinstance(obj, Explosion), obj.y if obj else 0)

        all_objs.sort(key=sort_key)
        all_objs.append(self.flying_enemy)

        for obj in all_objs:
            if obj:
                obj.draw()

    def play_sound(self, name, count=1):
        if self.player:
            try:
                sound = getattr(sounds, name + str(randint(0, count - 1)))
                sound.play()
            except Exception as e:
                print(e)

def space_pressed():
    global space_down
    if keyboard.space:
        if not space_down:
            space_down = True
            return True
    else:
        space_down = False
        return False

class State(Enum):
    MENU = 1,
    PLAY = 2,
    GAME_OVER = 3

def update():
    global state, game

    if state == State.MENU:
        if space_pressed():
            state = State.PLAY
            game = Game(Player((240, 768)))

        game.update()

    elif state == State.PLAY:
        if game.player.lives == 0 and game.player.timer == 100:
            sounds.gameover.play()
            sstate = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if space_pressed():
            state = State.MENU
            game = Game()

def draw():
    game.draw()

    if state == State.MENU:
        screen.blit("title", (0,0))
        screen.blit("space" + str((game.time // 4) % 14), (0, 240))

    elif state == State.PLAY:
        for i in range(game.player.lives):
            screen.blit("life", (i*40+8, 4))

        score = str(game.score)

        for i in range(1, len(score)+1):
            digit = score[-i]
            screen.blit("digit"+digit, (468-i*24, 5))

    elif state == State.GAME_OVER:
        screen.blit("over", (0,0))

state = State.MENU
game = Game()

#----------------------
from engine import run
run()
