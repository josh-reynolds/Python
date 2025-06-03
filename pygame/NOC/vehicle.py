import math
from random import uniform
import pygame
from pygame.locals import SRCALPHA
from pygame import Rect, Surface, transform
from engine import *
from pvector import PVector

class Vehicle:
    def __init__(self, x, y, max_width, max_height):
        self.location = PVector(x,y)
        width = 20
        height = 80
        self.max_width = max_width
        self.max_height = max_height
        self.rect = Rect(x - width/2, y - height/2, 20, 80)
        self.color = (0, 200, 0)
        
        self.surf = Surface((self.rect.width, self.rect.height), flags=SRCALPHA)
        pygame.draw.rect(self.surf, self.color, (0, 0, width, height), width=0) 
        pygame.draw.rect(self.surf, (0,0,0), (0, 0, width, height), width=1) 
        pygame.draw.circle(self.surf, (0,0,0), (10,10), 10, 0)
        self.original_surf = self.surf.copy()

        self.velocity = PVector(0,0)
        self.acceleration = PVector(0,0)

        self.r = 3.0
        self.maxspeed = 4
        self.maxforce = 0.1

        self.angle = 0

        self.target = PVector(0,0)

    def update(self):
        self.velocity + self.acceleration
        self.velocity.limit(self.maxspeed)
        self.location + self.velocity
        self.acceleration * 0

        prev_angle = self.angle % 360
        to_target = PVector.sub(self.target, self.location).normalize()
        screen.draw.line((0,0,0), (self.location.x, self.location.y), (self.target.x, self.target.y))

        pa = math.radians(prev_angle)
        angle_x = self.location.x + math.cos(pa) * 100
        angle_y = self.location.y + math.sin(pa) * 100
        screen.draw.line((255,0,0), (self.location.x, self.location.y), (angle_x, angle_y))

        target_angle = to_target.heading()
        if target_angle < 0:
            target_angle += 360

        delta = (target_angle - prev_angle)
        if delta > 180:
            delta = -(360 - delta)
        if delta < -180:
            delta = 360 + delta

        adjust = 0
        if delta > 1:
            adjust = 3
        elif delta < -1:
            adjust = -3

        self.angle = prev_angle + adjust
        self.rotate()

    def draw(self):
        screen.blit(self.surf, (self.rect.x, self.rect.y))

    def apply_force(self, force):
        self.acceleration + force

    def wander(self):
        projected_distance = 100
        angle_x = self.location.x + math.cos(math.radians(self.angle)) * projected_distance
        angle_y = self.location.y + math.sin(math.radians(self.angle)) * projected_distance
        #screen.draw.circle(angle_x, angle_y, 10, (0,255,0))
        predicted = PVector(angle_x, angle_y)

        r = 50
        #screen.draw.circle(angle_x, angle_y, r, (0,0,0), 1)
        random_angle = uniform(0,360)
        target_x = angle_x + math.cos(math.radians(random_angle)) * r
        target_y = angle_y + math.sin(math.radians(random_angle)) * r
        #screen.draw.circle(target_x, target_y, 5, (0,255,0))

        boundary = 25
        if target_x > self.max_width - boundary:
            target_x = self.max_width//2
        if target_x < boundary:
            target_x = self.max_width//2
        if target_y > self.max_height - boundary:
            target_y = self.max_height//2
        if target_y < boundary:
            target_y = self.max_height//2

        self.seek(PVector(target_x, target_y))

    def seek(self, target):
        self.target = target
        d = PVector.sub(target, self.location)
        distance = d.mag()
        desired = PVector.normalize(d)

        if distance < 100:
            m = remap(distance, 0, 100, 0, self.maxspeed)
            desired * m
        else:
            desired * self.maxspeed

        steer = PVector.sub(desired, self.velocity)
        steer.limit(self.maxforce)
        self.apply_force(steer)

    def rotate(self):
        self.surf = transform.rotate(self.original_surf, -self.angle - 90)
        w,h = self.surf.get_size()
        self.rect = Rect(self.location.x-w/2, self.location.y-h/2, w, h)

    def follow(self, field):
        int_location = PVector(int(self.location.x), int(self.location.y))
        desired = field.lookup(int_location)
        desired * self.maxspeed
        steer = PVector.sub(desired, self.velocity)
        steer.limit(self.maxforce)
        self.apply_force(steer)

    def track(self, path):
        predict = self.velocity.normalize()
        predict * 25
        predict_loc = PVector.add(self.location, predict)

        screen.draw.circle(predict_loc.x, predict_loc.y, 25, (255,0,0))

        normal_point = Vehicle.get_normal_point(predict_loc, path.start, path.end)

        screen.draw.circle(normal_point.x, normal_point.y, 15, (0,0,255))

        direction = PVector.sub(path.end, path.start)
        direction = direction.normalize()
        direction * 10
        target = PVector.add(normal_point, direction)

        distance = PVector.dist(predict_loc, normal_point)
        if distance > path.radius:
            #self.seek(target)   # always positive direction, so moves offscreen
            self.seek(normal_point) # this one will turn back

    def get_normal_point(p, a, b):
        ap = PVector.sub(p, a)
        ab = PVector.sub(b, a)

        ab = ab.normalize()
        ab * ap.dot(ab)

        normal_point = PVector.add(a, ab)
        return normal_point

    def accelerate(self, amount):
        a = math.radians(self.angle)
        angle_x = self.location.x - math.cos(a) * amount
        angle_y = self.location.y - math.sin(a) * amount
        force = PVector.sub(self.location, PVector(angle_x,angle_y))
        self.apply_force(force)

# BUG FIX NOTES ~~~~~~~~~~~~~~~~~~
# The heading code isn't working properly, needs debugging
# I added some line indicators to see what's going on.
# Observed bugs:
#   [FIXED] Drawing orientation doesn't align with heading vector, and is inconsistent
#   [FIXED] Drawing rotates opposite direction from heading vector
#   [FIXED] Heading vector properly moves toward target only in lower two quadrants (PI to TWO_PI)
#     spins indefinitely conterclockwise in upper two without stopping on target
#   [FIXED] Rotation calculation doesn't properly handle crossing 0/360 degree boundary,
#     will take the long way around

# If we take out the sprite rotation, can see cause of first bug: it is using the 
# top-left corner of the image rect as axis - need to center this
# also, current drawing orientation is pointing down - either adapt or fix

# As for the quadrants, the top two return angles of 0 to -180, and the bottom
# return angles of 0 to 180 - need to adjust or accommodate in order to correct

# So, the heading calculation is just math.atan2(), which:
#   is oriented vertically (0 degrees is up)
#   returns positive values for the right-hand quadrants (+x,+y) and (+x,-y)
#   returns negative values for the left-hand quadrants (-x,+y) and (-x,-y)

# The vehicle angle is counting 0 to 360 degrees clockwise, oriented to the right:
#   0/360 degrees is (+x,0y)
#   90 degrees is (0x,-y)
#   180 degrees is (-x,0y))
#   270 degrees is (0x,+y)
# The current motion of the pointer, however, is counter-clockwise (decrementing angle)

# Fixed the quadrant problem, but that introduced a new issue: the delta always takes
# the long away around the circle - it can't cross the 0/360 boundary

# Instead of forcing atan values to 0-360 range, perhaps it's better to use the 
# +/- 180 range, which would indicate direction. Also could shift towards relative
# rather than absolute angles...
