"""Contains classes and functions to handle a screen projection matrix."""

# TO_DO: note proper usage in comments - clients should make use of the
#        helper functions and not directly interact with the ScreenMatrix
#        instance in most circumstances.

import math
from engine import screen
from pvector import PVector

class ScreenMatrix:
    """Represents a screen projection matrix."""

    def __init__(self):
        """Create an instance of a ScreenMatrix."""
        self.origin = PVector(0,0)
        self.color = (0,0,0)
        self.angle = 0
        self.stack = []

    def __repr__(self):
        """Return the developer string representation of a ScreenMatrix."""
        return f"({self.origin.x:0.2f}, {self.origin.y:0.2f}) {self.angle:0.2f} : {self.stack}"

    def reset(self):
        """Reset all changes to the current ScreenMatrix."""
        self.origin = PVector(0,0)
        self.color = (0,0,0)
        self.angle = 0
        self.stack = []

    def translate(self, target):
        """Apply a translation to the ScreenMatrix."""
        target.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        self.origin + target

    def rotate(self, radians):
        """Apply a rotation to the ScreenMatrix."""
        self.angle += radians

    def push_matrix(self):
        """Save the current state of the ScreenMatrix to a stack."""
        self.stack.append((self.origin.copy(), self.angle))

    def pop_matrix(self):
        """Recall the most recent previous state of the ScreenMatrix from the stack."""
        if len(self.stack) > 0:
            self.origin, self.angle = self.stack.pop()

    def draw_line(self, start, end, width=1):
        """Draw a line on the screen, applying the ScreenMatrix transforms."""
        s = PVector(*start)
        s.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        s + self.origin

        e = PVector(*end)
        e.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        e + self.origin

        screen.draw.line(self.color, (s.x, s.y), (e.x, e.y), width)

    def draw_circle(self, x, y, radius, color, width=0):
        """Draw a circle on the screen, applying the ScreenMatrix transforms."""
        o = PVector(x,y)
        o.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        o + self.origin

        screen.draw.circle(o.x, o.y, radius, color, width)

    def draw_rect(self, x, y, w, h, color, width=0):
        """Draw a rectangle on the screen, applying the ScreenMatrix transforms."""
        top_left = PVector(x,y)
        top_left.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        top_left + self.origin
        t_l = (top_left.x, top_left.y)

        top_right = PVector(x+w,y)
        top_right.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        top_right + self.origin
        t_r = (top_right.x, top_right.y)

        bottom_left = PVector(x,y+h)
        bottom_left.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        bottom_left + self.origin
        b_l = (bottom_left.x, bottom_left.y)

        bottom_right = PVector(x+w,y+h)
        bottom_right.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        bottom_right + self.origin
        b_r = (bottom_right.x, bottom_right.y)

        screen.draw.polygon((t_l, t_r, b_r, b_l), color, width)

    def draw_triangle(self, x_1, y_1, x_2, y_2, x_3, y_3, color, width=0):
        """Draw a triangle on the screen, applying the ScreenMatrix transforms."""
        first = PVector(x_1, y_1)
        first.rotate(math.degrees(self.angle))
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        first + self.origin
        f = (first.x, first.y)

        second = PVector(x_2, y_2)
        second.rotate(math.degrees(self.angle))
        second + self.origin
        s = (second.x, second.y)

        third = PVector(x_3, y_3)
        third.rotate(math.degrees(self.angle))
        third + self.origin
        t = (third.x, third.y)

        screen.draw.polygon((f, s, t), color, width)

    def draw_polygon(self, points, color, width=0):
        """Draw a polygon on the screen, applying the ScreenMatrix transforms."""
        vertices = []
        for p in points:
            point = PVector(p[0], p[1])
            point.rotate(math.degrees(self.angle))
            # pylint: disable=W0104
            # W0104: Statement seems to have no effect (pointless-statement)
            point + self.origin
            vertices.append((point.x, point.y))

        screen.draw.polygon(vertices, color, width)


def translate(x, y):
    """Apply the PVector as a translation to the ScreenMatrix."""
    sm.translate(PVector(x,y))

def rotate(radians):
    """Apply the specified value as a rotation to the ScreenMatrix."""
    sm.rotate(radians)

def push_matrix():
    """Save the current state of the ScreenMatrix to a stack."""
    sm.push_matrix()

def pop_matrix():
    """Recall the most recent previous state of the ScreenMatrix from the stack."""
    sm.pop_matrix()

def line(a_x, a_y, b_x, b_y, line_weight=1):
    """Draw a line on the screen, applying the ScreenMatrix transforms."""
    sm.draw_line((a_x, a_y), (b_x, b_y), line_weight)

def circle(x, y, r, color=(0,0,0), width=1):
    """Draw a circle on the screen, applying the ScreenMatrix transforms."""
    sm.draw_circle(x, y, r, color, width)

# TO_DO: need to implement rect mode, current implementation
#        is equivalent to CORNERS
def rect(x, y, w, h, color=(0,0,0), width=1):
    """Draw a rectangle on the screen, applying the ScreenMatrix transforms."""
    sm.draw_rect(x, y, w, h, color, width)

def triangle(x_1, y_1, x_2, y_2, x_3, y_3, color=(0,0,0), width=1):
    """Draw a triangle on the screen, applying the ScreenMatrix transforms."""
    sm.draw_triangle(x_1, y_1, x_2, y_2, x_3, y_3, color, width)

# TO_DO: should we shift to this model for all regular
#        figures, rather than have the client figure out
#        all the vertices?
#
#        shape drawing should create a figure of the desired
#        configuration at the origin - use translate() & rotate()
#        to place it
def equilateral_triangle(radius, color=(0,0,0), width=1):
    """Draw an equilateral triangle on the screen, applying the ScreenMatrix transforms."""
    sides = 3
    tri_points = []
    for i in range(sides):
        angle = math.pi * 2/sides * (i+1)
        v_x = radius * math.cos(angle)
        v_y = radius * math.sin(angle)
        tri_points.append(v_x)
        tri_points.append(v_y)

    triangle(*tri_points, color, width)

def polygon(points, color=(0,0,0), width=1):
    """Draw a polygon on the screen, applying the ScreenMatrix transforms."""
    sm.draw_polygon(points, color, width)

sm = ScreenMatrix()
