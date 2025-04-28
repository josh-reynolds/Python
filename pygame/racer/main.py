import math
import platform
from enum import Enum
import pygame
from pygame.math import Vector2, Vector3
from engine import *

WIDTH = 400
HEIGHT = 400
TITLE = "Racer"

FIXED_TIMESTEP = 1 ###
CLIPPING_PLANE = -1 ###
SPACING = 1 ###
VIEW_DISTANCE = 1 ###
HALF_STRIPE_W = 1 ###
HALF_RUMBLE_STRIP_W = 1 ###
HALF_YELLOW_LINE_W = 1 ###
YELLOW_LINE_EDGE_DISTANCE = 1
SHOW_SCENERY = True  ###

SPECIAL_FONT_SYMBOLS = {'xb_a':'%'}

fade_to_black_image = pygame.Surface((WIDTH,HEIGHT))

def inverse_lerp(a, b, c): ###
    return 1 ###

def draw_text(a, b, c, d): ###
    pass ###

class KeyboardControls:
    def update(self):
        pass ###
    def button_pressed(self, a):  ###
        pass ###
class TrackPiece:
    def __init__(self): ###
        self.width = 1 ###
        self.offset_x = 1 ###
        self.offset_y = 1 ###
        self.scenery = [] ###
        self.cars = [] ###

def make_track():
    return (TrackPiece(), TrackPiece(), TrackPiece()) ###

class Game:
    def __init__(self, controls=None):
        self.track = make_track()
        self.player_car = None
        self.camera_follow_car = None
        self.setup_cars(controls)
        self.camera = Vector3(0, 400, 0)
        self.background = images.background
        self.bg_offset = Vector2(-self.background.get_width() // 2, 30)
        self.first_frame = True
        self.frame_counter = 0
        self.timer = 0
        self.race_complete = False
        self.time_up = False
        if self.player_car is not None:
            self.start_timer = 3.999
            play_music("engines_startline")
        else:
            self.start_timer = 0

    def setup_cars(self, a): ###
        pass ###
    def update(self, a): ###
        pass ###

    def draw(self):
        if self.bg_offset.y > 0:
            screen.fill( (0,20,117) )
        else:
            screen.fill( (0,77,180) )

        screen.blit(self.background, self.bg_offset)
        bg_width = self.background.get_width()
        if self.bg_offset.x > 0:
            screen.blit(self.background, self.bg_offset - Vector2(bg_width, 0))
        if self.bg_offset.x + self.background.get_width() < WIDTH:
            screen.blit(self.background, self.bg_offset + Vector2(bg_width, 0))

        def transform(point_v3, w=None, h=None, clipping_plane=CLIPPING_PLANE):
            newpoint = point_v3 - self.camera
            if newpoint.z > clipping_plane:
                return None if w is None else (None, None, None)

            point_v2 = pygame.math.Vector2((newpoint.x / newpoint.z) + HALF_WIDTH,
                                           (newpoint.y / newpoint.z) + HALF_HEIGHT)

            if w is None:
                return point_v2
            else:
                return point_v2, w / -newpoint.z, h / -newpoint.z

        offset = Vector3(0,0,0)
        offset_delta = Vector3(0,0,0)

        prev_track_screen = None
        prev_stripe_screen = None
        prev_rumble_left_outer_screen = None
        prev_rumble_right_outer_screen = None

        draw_list = []

        def add_to_draw_list(drawcall, type="?"):
            draw_list.append((drawcall, type))

        is_first_track_piece_ahead = True

        result = self.get_first_track_piece_ahead(self.camera.z)

        first_track_piece_idx, current_piece_z = result
        track_ahead_i = 0
        current_piece_z += SPACING

        for i in range(first_track_piece_idx, len(self.track)):
            track_ahead_i += 1
            if track_ahead_i > VIEW_DISTANCE:
                break

            track_piece = self.track[i]
            current_piece_z -= SPACING

            left = Vector3(track_piece.width / 2, 0, current_piece_z)
            right = Vector3(-track_piece.width / 2, 0, current_piece_z)

            if is_first_track_piece_ahead:
                adjusted_camera_z = self.camera.z - SPACING
                fraction = inverse_lerp(current_piece_z - SPACING, current_piece_z, adjusted_camera_z)
                offset_delta = Vector3(fraction * track_piece.offset_x,
                                       fraction * track_piece.offset_y, 0)
            else:
                offset_delta += Vector3(track_piece.offset_x, track_piece.offset_y, 0)

            is_first_track_piece_ahead = False

            offset += offset_delta
            left += offset
            right += offset

            left_screen = transform(left)
            right_screen = transform(right)

            stripe_left = Vector3(HALF_STRIPE_W, 0, current_piece_z) + offset
            stripe_right = Vector3(-HALF_STRIPE_W, 0, current_piece_z) + offset
            stripe_left_screen = transform(stripe_left)
            stripe_right_screen = transform(stripe_right)

            rumble_strip_left_outer = left + Vector3(HALF_RUMBLE_STRIP_W, 0, 0)
            rumble_strip_right_outer = right - Vector3(HALF_RUMBLE_STRIP_W, 0, 0)
            rumble_strip_left_outer_screen = transform(rumble_strip_left_outer)
            rumble_strip_right_outer_screen = transform(rumble_strip_right_outer)

            yellow_left_outer = left - Vector3(YELLOW_LINE_EDGE_DISTANCE, 0, 0)
            yellow_left_inner = yellow_left_outer - Vector3(HALF_YELLOW_LINE_W, 0, 0)
            yellow_right_outer = right + Vector3(YELLOW_LINE_EDGE_DISTANCE, 0, 0)
            yellow_right_inner = yellow_right_outer - Vector3(HALF_YELLOW_LINE_W, 0, 0)
            yellow_line_left_outer_screen = transform(yellow_left_outer)
            yellow_line_left_inner_screen = transform(yellow_left_inner)
            yellow_line_right_outer_screen = transform(yellow_right_outer)
            yellow_line_right_inner_screen = transform(yellow_right_inner)

            if left_screen is not None and right_screen is not None:
                if prev_track_screen is not None:
                    def any_on_screen(points):
                        on_screen = [point for point in points if point[1] < HEIGHT]
                        return any(on_screen)

                    def draw_polygon(points, col):
                        pygame.draw.polygon(screen.surface, col, points, OUTLINE_W)

                    def draw_points(points, col):
                        if any_on_screen(points):
                            add_to_draw_list(lambda col=col, points=points: draw_polygon(points, col))

                    if i // 3 % 2 == 0:
                        points = (stripe_left_screen, stripe_right_screen,
                                  prev_stripe_screen[1], prev_stripe_screen[0])
                        draw_points(points, STRIPE_COLOR)

                    if SHOW_YELLOW_LINES:
                        left_yellow_line_points = (prev_yellow_line_left_outer_screen,
                                                   yellow_line_left_outer_screen,
                                                   yellow_line_left_inner_screen,
                                                   prev_yellow_line_left_inner_screen)
                        draw_points(left_yellow_line_points, YELLOW_LINE_COL)

                        right_yellow_line_points = (prev_yellow_line_right_outer_screen,
                                                   yellow_line_right_outer_screen,
                                                   yellow_line_right_inner_screen,
                                                   prev_yellow_line_right_inner_screen)
                        draw_points(right_yellow_line_points, YELLOW_LINE_COL)

                    points = (prev_track_screen[0], left_screen, right_screen, prev_track_screen[1])
                    draw_points(points, track_piece.col)

                    if SHOW_RUMBLE_STRIPS:
                        rumble_col = RUMBLE_COL_1 if (i // 2) % 2 == 0 else RUMBLE_COL_2
                        rumble_left_points = (prev_rumble_left_outer_screen,
                                              prev_track_screen[0],
                                              left_screen,
                                              rumble_strip_left_outer_screen)
                        rumble_right_points = (prev_rumble_right_outer_screen,
                                              prev_track_screen[1],
                                              right_screen,
                                              rumble_strip_right_outer_screen)
                        draw_points(rumble_left_points, rumble_col)
                        draw_points(rumble_right_points, rumble_col)

                    if SHOW_TRACKSIDE:
                        trackside_col = TRACKSIDE_COLOR_1 if (i // 5) % 2 == 0 else TRACKSIDE_COLOR_2
                        trackside_left_points = (points[2], points[3],
                                                 (0, points[3].y),
                                                 (0, points[2].y))
                        trackside_right_points = (points[0], points[1],
                                                 (WIDTH - 1, points[1].y),
                                                 (WIDTH - 1, points[0].y))
                        draw_points(trackside_left_points, trackside_col)
                        draw_points(trackside_right_points, trackside_col)

                prev_track_screen = (left_screen, right_screen)
                prev_stripe_screen = (stripe_left_screen, stripe_right_screen)
                prev_rumble_left_outer_screen = rumble_strip_left_outer_screen
                prev_rumble_right_outer_screen = rumble_strip_right_outer_screen
                prev_yellow_line_left_outer_screen = yellow_line_left_outer_screen
                prev_yellow_line_left_inner_screen = yellow_line_left_inner_screen
                prev_yellow_line_right_outer_screen = yellow_line_right_outer_screen
                prev_yellow_line_right_inner_screen = yellow_line_right_inner_screen

            if SHOW_SCENERY:
                for obj in track_piece.scenery:
                    if track_ahead_i * SPACING < obj.max_draw_distance:
                        pos_v3 = Vector3(obj.x, 0, current_piece_z) + offset
                        if self.camera.z - current_piece_z > obj.min_draw_distance:
                            billboard = obj.get_image()
                            w, h = billboard.get_width(), billboard.get_height()
                            pos, scaled_w, scaled_h = transform(pos_v3, w * obj_scale, h * obj_scale)
                            if pos is not None and scaled_w < MAX_SCENERY_SCALED_WIDTH:
                                pos -= Vector2(scaled_w // 2, scaled_h)
                                try:
                                    scaled_w, scaled_h = int(scaled_w), int(scaled_h)
                                    scaled = SCALE_FUNC(billboard, (scaled_w, scaled_h))
                                    add_to_draw_list(lambda scaled=scaled, pos=pos: screen.blit(scaled, pos))
                                except pygame.error:
                                    print(f"SCALE ERROR, w/h: {scaled_w} {scaled_h}")

            cars_to_draw = []
            for car in track_piece.cars:
                car_offset = Vector3(offset)
                if car.pos.z % SPACING != 0:
                    fraction = inverse_lerp(current_piece_z, current_piece_z - SPACING, car.pos.z)
                    next_track_piece = self.track[i+1]
                    car_offset += Vector3(fraction * next_track_piece.offset_x,
                                          fraction * next_track_piece.offset_y,
                                          -fraction * SPACING)
                    car_offset += offset_delta * fraction

                if car is self.camera_follow_car:
                    car_offset.x = 0
                    car_offset.y = 0

                pos_v3 = Vector3(car.pos.x, 0, current_piece_z) + car_offset
                scale = 2

                if isinstance(car, CPUCar):
                    z_distance = max(1, -(pos_v3.z - self.camera.z))
                    offset_for_angle = (pos_v3.x - self.camera.x) / z_distance
                    offset_for_angle += -car.steering * 10
                    angle_sprite_idx = int(remap_clamp(offset_for_angle, -200, 200, -4, 4))

                    if car is self.camera_follow_car:
                        angle_sprite_idx = min(max(angle_sprite_idx, -1), 1)

                    car.update_sprite(angle_sprite_idx, braking=False)

                img = getattr(images, car.image)
                pos, scaled_w, scaled_h = transform(pos_v3, 
                                                    img.get_width() * scale,
                                                    img.get_height() * scale,
                                                    clipping_plane=CLIPPING_PLANE_CARS)

                if pos is not None and scaled_w < MAX_CAR_SCALED_WIDTH:
                    pos -= Vector2(scaled_w // 2, scaled_h)
                    scaled = SCALE_FUNC(img, (int(scaled_w), int(scaled_h)))
                    cars_to_draw.append({"z": car.pos.z, 
                                         "drawcall": lambda scaled=scaled, pos=pos: screen.blit(scaled, pos)})

            cars_to_draw.sort(key=lambda entry: entry["z"], reverse=True)
            for entry in cars_to_draw:
                add_to_draw_list(entry["drawcall"], "cars")

        for draw_call, type in reversed(draw_list):
            draw_call()

        if self.player_car is not None:
            player_pos = self.cars.index(self.player_car) + 1
            if self.time_up:
                draw_text("TIME UP!", WIDTH // 2, HEIGHT * 0.4, center=True)
            elif self.race_complete:
                fastest_lap_str = format_time(self.player_car.fastest_lap)
                race_time_str = format_time(self.player_car.race_time)
                draw_text("RACE COMPLETE!", WIDTH // 2, HEIGHT * 0.15, center=True)
                draw_text("POSITION", WIDTH // 2, HEIGHT * 0.3, center=True)
                draw_text(str(player_pos), WIDTH // 2, HEIGHT * 0.42, center=True)
                draw_text("FASTEST LAP", WIDTH * 0.25, HEIGHT * 0.55, center=True)
                draw_text(fastest_lap_str, WIDTH * 0.25, HEIGHT * 0.68, center=True)
                draw_text("RACE TIME", WIDTH * 0.75, HEIGHT * 0.55, center=True)
                draw_text(race_time_str, WIDTH * 0.75, HEIGHT * 0.68, center=True)
            else:
                status_x = (WIDTH/2) - (565/2)
                speed_str = f"{int(self.player_car.speed):03}"
                lap_time_str = format_time(self.player_car.lap_time)
                screen.blit("status", (status_x, 0))
                draw_text(f"{self.player_car.lap:02}", status_x + 30, 37, font="status1b_")
                draw_text(f"{player_pos:02}", status_x + 116, 37, font="status1b_")
                draw_text(speed_str, status_x + 197, 37, font="status1b_")
                draw_text(lap_time_str, status_x + 299, 37, font="status2_")

                if self.player_car.last_lap_was_fastest and self.player_car.lap_time < 4:
                    y = HEIGHT * 0.4
                    draw_text("FASTEST LAP!", WIDTH // 2, y, center=True)
                    draw_text(format_time(self.player_car.fastest_lap), WIDTH // 2, y + 60, center=True)

                if self.player_car.last_lap_was_fastest:
                    begin_time, end_time = 4, 8
                else:
                    begin_time, end_time = 0, 4
                if self.player_car.lap == NUM_LAPS and begin_time < self.player_car.lap_time < end_time:
                    y = HEIGHT * 0.4
                    draw_text("FINAL LAP!", WIDTH // 2, y, center=True)

    def get_first_track_piece_ahead(self, z):
        idx = -int(math.floor(z / SPACING))
        first_piece_z = -idx * SPACING
        if idx >= len(self.track):
            return None,None
        else:
            return idx, first_piece_z

def update_controls():
    keyboard_controls.update()

class State(Enum):
    TITLE = 1

### REMINDER: still need to implement delta time calculation in the engine
def update(delta_time):
    global state, game, accumulated_time, demo_reset_timer, demo_start_timer

    update_controls()

    def button_pressed_controls(button_num):
        for controls in (keyboard_controls,):
            if controls is not None and controls.button_pressed(button_num):
                return controls
        return None

    if state == State.TITLE:
        controls = button_pressed_controls(0)
        if controls is not None:
            state = State.PLAY
            game = Game(controls)

        demo_reset_timer -= delta_time
        demo_start_timer += delta_time
        if demo_reset_timer <= 0:
            game = Game()
            demo_reset_timer = 60 * 2
            demo_start_timer = 0

    elif state == State.PLAY:
        if game.race_complete:
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        if button_pressed_controls(0) is not None:
            game.player_car.stop_engine_sound()
            state = State.TITLE
            game = Game()
            play_music("title_theme")

    accumulated_time += delta_time
    while accumulated_time >= FIXED_TIMESTEP:
        accumulated_time -= FIXED_TIMESTEP
        game.update(FIXED_TIMESTEP)

def draw():
    game.draw()

    if state == State.TITLE:
        if demo_reset_timer < 1 or demo_start_timer < 1:
            value = demo_reset_timer if demo_reset_timer < 1 else demo_start_timer
            alpha = min(255, 255-(value*255))
            fade_to_black_image.set_alpha(alpha)
            fade_to_black_image.fill((0,0,0))
            screen.blit(fade_to_black_image, (0,0))

        text = f"PRESS {SPECIAL_FONT_SYMBOLS['xb_a']} OR" \
               f"{'Z' if 'Darwin' in platform.version() else 'LEFT CONTROL'}"
        draw_text(text, WIDTH // 2, HEIGHT - 82, True)

        logo_img = images.logo
        screen.blit(logo_img, (WIDTH//2 - logo_img.get_width() // 2,
                               HEIGHT//3 - logo_img.get_height() // 2))

keyboard_controls = KeyboardControls()
state = State.TITLE
game = Game()
demo_reset_timer, demo_start_timer = 2 * 60, 0
accumulated_time = 0

run()
