import sys
from enum import Enum
from random import random, randint, choice
from engine import keyboard, Actor, sounds, music

if sys.version_info < (3,6):
    print("This game requires at least version 3.6 of Python. Please download"
          "it from www.python.org")
    sys.exit()

engine = sys.modules["engine"]
engine_version = [int(s) if s.isnumeric() else s
                  for s in engine.__version__.split('.')]

if engine_version < [0,4]:
    print(f"This game requires at least version 0.4 of the engine. "
          f"You are using version {engine.__version__}. Please upgrade.")
    sys.exit()

WIDTH = 480
HEIGHT = 800
TITLE = "Bugz!"

DEBUG_TEST_RANDOM_POSITIONS = False
CENTER_ANCHOR = ("center","center")

num_grid_rows = 25
num_grid_cols = 14

def pos2cell(x, y):
    return ((int(x)-16)//32, int(y)//32)

def cell2pos(cell_x, cell_y, x_offset=0, y_offset=0):
    return [(cell_x * 32) + 32 + x_offset, (cell_y * 32) + 16 + y_offset]

class Explosion(Actor):
    def __init__(self, pos, exp_type):
        super().__init__("blank", pos)
        self.type = exp_type
        self.timer = 0

    def update(self):
        self.timer += 1
        self.image = "exp" + str(self.type) + str(self.timer // 4)

class Player(Actor):
    INVULNERABILITY_TIME = 100
    RESPAWN_TIME = 100
    RELOAD_TIME = 10

    def __init__(self, pos):
        super().__init__("blank", pos)
        self.direction = 0
        self.frame = 0
        self.lives = 3
        self.alive = True
        self.timer = 0
        self.fire_timer = 0

    def move(self, dx, dy, speed):
        for i in range(speed):
            if game.allow_movement(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy

    def update(self):
        self.timer += 1

        if self.alive:
            dx = 0
            if keyboard.left:
                dx = -1
            elif keyboard.right:
                dx = 1

            dy = 0
            if keyboard.up:
                dy = -1
            elif keyboard.down:
                dy = 1

            self.move(dx, 0, 3 - abs(dy))
            self.move(0, dy, 3 - abs(dx))
            directions = [7,0,1,6,-1,2,5,4,3]
            direction = directions[dx+3*dy+4]

            if self.timer % 2 == 0 and direction >= 0:
                difference = (direction - self.direction)
                rotation_table = [0, 1, 1, -1]
                rotation = rotation_table[difference % 4]
                self.direction = (self.direction + rotation) % 4

            self.fire_timer -= 1

            if self.fire_timer < 0 and (self.frame > 0 or keyboard.space):
                if self.frame == 0:
                    game.play_sound("laser")
                    game.bullets.append(Bullet((self.x, self.y - 8)))
                self.frame = (self.frame + 1) % 3
                self.fire_timre = Player.RELOAD_TIME

            all_enemies = game.segments + [game.flying_enemy]

            for enemy in all_enemies:
                if enemy and enemy.collidepoint(self.pos):
                    if self.timer > Player.INVULNERABILITY_TIME:
                        game.play_sound("player_explode")
                        game.explosions.append(Explosion(self.pos, 1))
                        self.alive = False
                        self.timer = 0
                        self.lives -= 1
        else:
            if self.timer > Player.RESPAWN_TIME:
                self.alive = True
                self.timer = 0
                self.pos = (240, 768)
                game.clear_rocks_for_respawn(*self.pos)

        invulnerable = self.timer > Player.INVULNERABILITY_TIME
        if self.alive and (invulnerable or self.timer % 2 == 0):
            self.image = "player" + str(self.direction) + str(self.frame)
        else:
            self.image = "blank"

class FlyingEnemy(Actor):
    def __init__(self, player_x):
        side = 1 if player_x < 160 else 0 if player_x > 320 else randint(0,1)
        super().__init__("blank", (550*side-35,688))
        self.moving_x = 1
        self.dx = 1 - 2 * side
        self.dy = choice([-1,1])         
        self.type = randint(0,2)
        self.health = 1
        self.timer = 0

    def update(self):
        self.timer += 1
        self.x += self.dx * self.moving_x * (3 - abs(self.dy))
        self.y += self.dy * (3 - abs(self.dx * self.moving_x))

        if self.y < 592 or self.y > 784:
            self.moving_x = randint(0,1)
            self.dy = -self.dy

        anim_frame = str([0,2,1,2][(self.timer // 4) % 4])
        self.image = "meanie" + str(self.type) + anim_frame

class Rock(Actor):
    def __init__(self, x, y, totem=False):
        anchor = (24,60) if totem else CENTER_ANCHOR
        super().__init__("blank", cell2pos(x,y), anchor=anchor)
        self.type = randint(0, 3)

        if totem:
            game.play_sound("totem_create")
            self.health = 5
            self.show_health = 5
        else:
            self.health = randint(3,4)
            self.show_health = 1
        
        self.timer = 1

    def damage(self, amount, damaged_by_bullet=False):
        if damaged_by_bullet and self.health == 5:
            game.play_sound("totem_destroy")
            game.score += 100
        else:
            if amount > self.health - 1:
                game.play_sound("rock_destroy")
            else:
                game.play_sound("hit", 4)

        game.explosions.append(Explosion(self.pos, 2 * (self.health == 5)))
        self.health -= amount
        self.show_health = self.health
        self.anchor, self.pos = CENTER_ANCHOR, self.pos

        return self.health < 1

    def update(self):
        self.timer += 1

        if self.timer % 2 == 1 and self.show_health < self.health:
            self.show_health += 1

        if self.health == 5 and self.timer > 200:
            self.damage(1)

        color = str(max(game.wave, 0) % 3)
        health = str(max(self.show_health - 1, 0))
        self.image = "rock" + color + str(self.type) + health

class Bullet(Actor):
    def __init__(self, pos):
        super().__init__("bullet", pos)
        self.done = False

    def update(self):
        self.y -= 24
        grid_cell = pos2cell(*self.pos)

        if game.damage(*grid_cell, 1, True):
            self.done = True
        else:
            for obj in game.segments + [game.flying_enemy]:
                if obj and obj.collidepoint(self.pos):
                    game.explosions.append(Explosion(obj.pos, 2))
                    obj.health -= 1

                    if isinstance(obj, Segment):
                        if obj.health == 0 \
                                and not game.grid[obj.cell_y][obj.cell_x] \
                                and game.allow_movement(game.player.x, game.player.y, 
                                                        obj.cell_x, obj.cell_y):
                                    rock = Rock(obj.cell_x, obj.cell_y, random() < 0.2)
                                    game.grid[obj.cell_y][obj.cell_x] = rock
                        game.play_sound("segment_explode")
                        game.score += 10
                    else:
                        game.play_sound("meanie_explode")
                        game.score += 20

                    self.done = True

                    return

SECONDARY_AXIS_SPEED = [0]*4 + [1]*8 + [2]*4
SECONDARY_AXIS_POSITIONS = [sum(SECONDARY_AXIS_SPEED[:i]) for i in range(16)]

DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]

def inverse_direction(direction):
    if direction == DIRECTION_UP:
        return DIRECTION_DOWN
    elif direction == DIRECTION_RIGHT:
        return DIRECTION_LEFT
    elif direction == DIRECTION_DOWN:
        return DIRECTION_UP
    elif direction == DIRECTION_LEFT:
        return DIRECTION_RIGHT

def is_horizontal(direction):
    return direction == DIRECTION_LEFT or direction == DIRECTION_RIGHT

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
        def inner(proposed_out_edge):
            new_cell_x = self.cell_x + DX[proposed_out_edge]
            new_cell_y = self.cell_y + DY[proposed_out_edge]

            out = new_cell_x < 0 or new_cell_x > num_grid_cols - 1 \
                    or new_cell_y > 0 or new_cell_y > num_grid_rows - 1

            turning_back_on_self = proposed_out_edge == self.in_edge
            direction_disallowed = proposed_out_edge == self.disallow_direction

            if out or (new_cell_y == 0 and new_cell_x < 0):
                rock = None
            else:
                rock = game.grid[new_cell_y][new_cell_x]

            rock_present = rock != None

            occupied_by_segment = (new_cell_x, new_cell_y) in game.occupied \
                    or (self.cell_x, self.cell_y, proposed_out_edge) in game.occupied

            if rock_present:
                horizontal_blocked = is_horizontal(proposed_out_edge)
            else:
                horizontal_blocked = not is_horizontal(proposed_out_edge)

            same_as_previous_x_direction = proposed_out_edge == self.previous_x_direction

            return (out, turning_back_on_self, direction_disallowed, occupied_by_segment,
                    rock_present, horizontal_blocked, same_as_previous_x_direction)

        return inner 

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

    def allow_movement(self, x, y, ax=-1, ay=-1):
        if x < 40 or x > 440 or y < 592 or y > 784:
            return False

        x0, y0 = pos2cell(x-18, y-10)
        x1, y1 = pos2cell(x+18, y+10)

        for yi in range(y0, y1+1):
            for xi in range(x0, x1+1):
                if self.grid[yi][xi] or xi == ax and yi == ay:
                    return False

        return True

    def clear_rocks_for_respawn(self, x, y):
        x0, y0 = pos2cell(x-18, y-10)
        x1, y1 = pos2cell(x+18, y+10)

        for yi in range(y0, y1+1):
            for xi in range(x0, x1+1):
                self.damage(xi, yi, 5)

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
                    x, y = randint(0, num_grid_cols-1), randint(1, num_grid_rows-3)
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

                    health = [[1,1],[1,2],[2,2],[1,1]][self.wave % 4][i % 2]
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

space_down = False

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
            state = State.GAME_OVER
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
        screen.blit("space" + str((game.time // 4) % 14), (0, 420))

    elif state == State.PLAY:
        for i in range(game.player.lives):
            screen.blit("life", (i*40+8, 4))

        score = str(game.score)

        for i in range(1, len(score)+1):
            digit = score[-i]
            screen.blit("digit"+digit, (468-i*24, 5))

    elif state == State.GAME_OVER:
        screen.blit("over", (0,0))

try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)

    music.play("theme")
    music.set_volume(0.4)
except:
    pass

state = State.MENU
game = Game()

#----------------------
from engine import run
run()
