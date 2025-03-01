import random
from enum import Enum
import pygame
from pygame.math import Vector2
from engine import keys, keyboard, music, sounds

WIDTH = 400    ###
HEIGHT = 400    ###
TITLE = "Futbol"

HALF_WINDOW_W = 100     ###
HALF_LEVEL_W = 100     ###
HALF_LEVEL_H = 100     ###
HALF_PITCH_H = 100     ###

LEVEL_W = 100   ###
LEVEL_H = 100   ###

LEAD_DISTANCE_1 = 100    ###

PLAYER_START_POS = [(0,0),(1,1),(2,2)]      ###


DEBUG_SHOW_LEADS = True                    ####
DEBUG_SHOW_TARGETS = False                    ####
DEBUG_SHOW_PEERS = True                    ####
DEBUG_SHOW_SHOOT_TARGET = True                    ####
DEBUG_SHOW_COSTS = True                    ####

class Mock:                 ###
    def __init__(self, child=False):       ###
        self.x = 1                 ###
        self.y = 1                 ###
        self.vpos = Vector2(0,0)         ###
        self.debug_target = Vector2(0,0)    ###
        self.lead = False                     ###
        self.team = 1                          ###
        if not child:                ###
            self.shadow = Mock(child=True)        ###
            self.owner = Mock(child=True)                  ###

    def update(self):                    ###
        pass                    ###

    def draw(self, a, b):            ###
        pass                         ###

class Difficulty:
    def __init__(self):                          ###
        self.goalie_enabled = False                      ###
        self.second_lead_enabled = False                      ###

DIFFICULTY = [Difficulty(),Difficulty(),Difficulty()]     ###

def cost(a, b):           ###
    return (0,0)           ###

def dist_key(a):                   ###
    return False                   ###

def safe_normalize(a):                ###
    return (Vector2(0,0),1)                      ###

class Player:                              ####
    def __init__(self, a, b, c):               ###
        self.peer = Mock(child=True)     ###
        self.shadow = Mock(child=True)        ###
        self.team = 1                          ###
        self.y = 1                 ###
        self.vpos = Vector2(0,0)         ###

    def update(self):                    ###
        pass                    ###

    def draw(self, a, b):            ###
        pass                         ###

class Goal:                   ###
    def __init__(self, a):    ###
        pass                  ###

    def draw(self, a, b):            ###
        pass                         ###

class Ball:                  ###
    def __init__(self):
        self.shadow = Mock(child=True)        ###
        self.vpos = Vector2(0,0)         ####
        self.owner = Mock(child=True)               ###
        self.y = 1                 ###

    def update(self):                    ###
        pass                    ###
    
    def draw(self, a, b):            ###
        pass                         ###

class Team:
    def __init__(self, controls):
        self.controls = controls
        self.active_control_player = None
        self.score = 0

    def human(self):
        return self.controls != None

class Game:
    def __init__(self, p1_controls=None, p2_controls=None, difficulty=2):
        self.teams = [Team(p1_controls), Team(p2_controls)] 
        self.difficulty = DIFFICULTY[difficulty]
        
        try:
            if self.teams[0].human():
                music.fadeout(1)
                sounds.crowd.play(-1)
                sounds.start.play()
            else:
                music.play("theme")
                sounds.crowd.stop()
        except Exception as e:                   #### temporary while implementing
            print(e)                             ###

        self.score_timer = 0 
        self.scoring_team = 1
        self.reset()

    def reset(self):
        self.players = []
        random_offset = lambda x: x + random.randint(-32,32)
        for pos in PLAYER_START_POS:
            self.players.append(Player(random_offset(pos[0]),
                                       random_offset(pos[1]), 0))
            self.players.append(Player(random_offset(LEVEL_W - pos[0]),
                                       random_offset(LEVEL_H - pos[1]), 1))

        for a, b in zip(self.players, self.players[::-1]):
            a.peer = b
                                                     
        self.goals = [Goal(i) for i in range(2)]
        self.teams[0].active_control_player = self.players[0]
        self.teams[1].active_control_player = self.players[1]
        other_team = 1 if self.scoring_team == 0 else 0
        self.kickoff_player = self.players[other_team]
        self.kickoff_player.vpos = Vector2(HALF_LEVEL_W - 30 + other_team * 60,
                                           HALF_LEVEL_H)
        self.ball = Ball()
        self.camera_focus = Vector2(self.ball.vpos)
        self.debug_shoot_target = None

    def update(self):
        self.score_timer -= 1

        if self.score_timer == 0:
            self.reset()

        elif self.score_timer < 0 and abs(self.ball.vpos.y - HALF_LEVEL_H) > HALF_PITCH_H:
            game.play_sound("goal", 2)
            self.scoring_team = 0 if self.ball.vpos.y < HALF_LEVEL_H else 1
            self.teams[self.scoring_team].score += 1
            self.score_timer = 60

        for b in self.players:
            b.mark = b.peer
            b.lead = None
            b.debug_target = None

        self.debug_shoot_target = None

        if self.ball.owner:
            o = self.ball.owner
            pos, team = o.vpos, o.team
            owners_target_goal = game.goals[team]
            other_team = 1 if team == 0 else 1

            if self.difficulty.goalie_enabled:
                nearest = min([p for p in self.players if p.team != team],
                              key=dist_key(owners_target_goal.vpos))

                o.peer.mark = nearest.mark
                nearest.mark = owners_target_goal

            l = sorted([p for p in self.players
                        if p.team != team
                        and p.timer <= 0
                        and (not self.teams[other_team].human()
                             or p != self.teams[other_team].active_control_player)
                        and not isinstance(p.mark, Goal)],
                       key=dist_key(pos))

            a = [p for p in l if (p.vpos.y > pos.y if team == 0
                                  else p.vpos.y < pos.y)]
            b = [p for p in l if p not in a]

            NONE2 = [None] * 2
            zipped = [s for t in zip(a+NONE2, b+NONE2) for s in t if s]

            # TO_DO: remove, only here temporarily to prevent a bug during development
            zipped = [Mock(),Mock()]      #####
            # ----------------------------------
            
            zipped[0].lead = LEAD_DISTANCE_1
            if self.difficulty.second_lead_enabled:
                zipped[1].lead = LEAD_DISTANCE_2

            self.kickoff_player = None

        for obj in self.players + [self.ball]:
            obj.update()

        owner = self.ball.owner

        for team_num in range(2):
            team_obj = self.teams[team_num]

            if team_obj.human() and team_obj.controls.shoot():
                def dist_key_weighted(p):
                    dist_to_ball = (p.vpos - self.ball.vpos).length()
                    goal_dir = (2 * team_num - 1)
                    if owner and (p.vpos.y - self.ball.vpos.y) * goal_dir < 0:
                        return dist_to_ball / 2
                    else:
                        return dist_to_ball

                self.teams[team_num].active_control_player = \
                        min([p for p in game.players
                             if p.team == team_num], key=dist_key_weighted)

        camera_ball_vec, distance = safe_normalize(self.camera_focus -
                                                   self.ball.vpos)

        if distance > 0:
            self.camera_focus -= camera_ball_vec * min(distance, 8)

    def draw(self):
        offset_x = max(0, min(LEVEL_W - WIDTH, self.camera_focus.x - WIDTH / 2))
        offset_y = max(0, min(LEVEL_H - HEIGHT, self.camera_focus.y - HEIGHT / 2))
        offset = Vector2(offset_x, offset_y)

        screen.blit("pitch",(-offset_x, -offset_y))

        objects = sorted([self.ball] + self.players, key=lambda obj: obj.y)
        objects = objects + [obj.shadow for obj in objects]
        objects = [self.goals[0]] + objects + [self.goals[1]]

        for obj in objects:
            obj.draw(offset_x, offset_y)

        for t in range(2):
            if self.teams[t].human():
                arrow_pos = self.teams[t].active_control_player.vpos - \
                        offset - Vector2(11, 45)
                screen.blit("arrow" + str(t), arrow_pos)

        if DEBUG_SHOW_LEADS:
            for p in self.players:
                if game.ball.owner and p.lead:
                    line_start = game.ball.owner.vpos - offset
                    line_end = p.vpos - offset
                    # Pygame Zero has draw.line, not sure why they chose to circumvent...
                    pygame.draw.line(screen.surface, (0,0,0), line_start, line_end)

        if DEBUG_SHOW_TARGETS:
            for p in self.players:
                line_start = p.debug_target - offset
                line_end = p.vpos - offset
                pygame.draw.line(screen.surface, (255,0,0), line_start, line_end)

        if DEBUG_SHOW_PEERS:
            for p in self.players:
                line_start = p.peer.vpos - offset
                line_end = p.vpos - offset
                pygame.draw.line(screen.surface, (0,0,255), line_start, line_end)

        if DEBUG_SHOW_SHOOT_TARGET:
            if self.debug_shoot_target and self.ball.owner:
                line_start = self.ball.owner.vpos - offset
                line_end = self.debug_shoot_target - offset
                pygame.draw.line(screen.surface, (255,0,255), line_start, line_end)

        if DEBUG_SHOW_COSTS:
            for x in range(0, LEVEL_W, 60):
                for y in range(0, LEVEL_H, 26):
                    c = cost(Vector2(x,y), self.ball.owner.team)[0]
                    screen_pos = Vector2(x,y) - offset
                    screen_pos = (screen_pos.x, screen_pos.y)
                    screen.draw.text(f"{c:.0f}", center=screen_pos)

key_status = {}

def key_just_pressed(key):
    result = False

    prev_status = key_status.get(key, False)

    if not prev_status and keyboard[key]:
        result = True

    key_status[key] = keyboard[key]

    return result

class Controls:
    def __init__(self, player_num):
        if player_num == 0:
            self.key_up = keys.UP
            self.key_down = keys.DOWN
            self.key_left = keys.LEFT
            self.key_right = keys.RIGHT
            self.key_shoot = keys.SPACE
        else:
            self.key_up = keys.W
            self.key_down = keys.S
            self.key_left = keys.A
            self.key_right = keys.D
            self.key_shoot = keys.LSHIFT

    def shoot(self):
        pass                          ###

class State(Enum):
    MENU = 0,
    PLAY = 1,
    GAME_OVER = 2

class MenuState(Enum):
    NUM_PLAYERS = 0,
    DIFFICULTY = 1

def update():
    global state, game, menu_state, menu_num_players, menu_difficulty

    if state == State.MENU:
        if key_just_pressed(keys.SPACE):
            if menu_state == MenuState.NUM_PLAYERS:
                if menu_num_players == 1:
                    menu_state = MenuState.DIFFICULTY
                else:
                    state = State.PLAY
                    menu_state = None
                    game = Game(Controls(0), Controls(1))
            else:
                state = State.PLAY
                menu_state = None
                game = Game(Controls(0), None, menu_difficulty)
        else:
            selection_change = 0
            if key_just_pressed(keys.DOWN):
                selection_change = 1
            elif key_just_pressed(keys.UP):
                selection_change = -1
            if selection_change != 0:
                sounds.move.play()
                if menu_state == MenuState.NUM_PLAYERS:
                    menu_num_players == 2 if menu_num_players == 1 else 1
                else:
                    menu_difficulty = (menu_difficulty + selection_change) % 3

        game.update()

    elif state == State.PLAY:
        if max([team.score for team in game.teams]) == 9 and game.score_timer == 1:
            state = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if key_just_pressed(keys.SPACE):
            state = State.MENU
            menu_state = MenuState.NUM_PLAYERS
            game = Game()

def draw():
    game.draw()

    if state == State.MENU:
        if menu_state == MenuState.NUM_PLAYERS:
            image = "menu0" + str(menu_num_players)
        else:
            image = "menu1" + str(menu_difficulty)
        screen.blit(image, (0,0))

    elif state == State.PLAY:
        screen.blit("bar", (HALF_WINDOW_W - 176, 0))

        for i in range(2):
            screen.blit("s" + str(game.teams[i].score), (HALF_WINDOW_W + 7 - 39 * i, 6))

        if game.score_timer > 0:
            screen.blit("goal", (HALF_WINDOW_W - 300, HEIGHT / 2 - 88 ))

    elif state == State.GAME_OVER:
        img = "over" + str(int(game.teams[1].score > game.teams[0].score))
        screen.blit(img, (0,0))

        for i in range(2):
            img = "l" + str(i) + str(game.teams[i].score)
            screen.blit(img, (HALF_WINDOW_W + 25 - 125 * i, 144))

state = State.MENU
menu_state = MenuState.NUM_PLAYERS
menu_num_players = 1
menu_difficulty = 0

game = Game()

#----------------------
from engine import run
run()

