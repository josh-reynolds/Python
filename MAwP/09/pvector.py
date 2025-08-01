import math
from random import uniform

class PVector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # instance methods ----------------------------
    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        self.x += other.x
        self.y += other.y

    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __mul__(self, scalar):
        self.x *= scalar
        self.y *= scalar

    def __truediv__(self, scalar):
        self.x /= scalar
        self.y /= scalar

    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y)

    def angle_between(self, other):
        dot = self.dot(other)
        return math.acos(dot / (self.mag() * other.mag()))

    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def limit(self, max_):
        m = self.mag()
        if m > max_:
            self / m
            self * max_

    def copy(self):
        return PVector(self.x, self.y)

    def heading(self):
        return math.degrees(math.atan2(self.y, self.x))

    def set_mag(self, m):
        p = self.normalize()
        p * m
        self.x, self.y = p.x, p.y

    def rotate(self, degrees):
        r = math.sqrt(self.x ** 2 + self.y ** 2)
        if self.x != 0:
            theta = math.atan2(self.y, self.x)
        else:
            if self.y > 0:
                theta = math.pi/2
            elif self.y < 0:
                theta = -math.pi/2
            else:
                theta = 0

        new_theta = theta + math.radians(degrees)

        self.x = r * math.cos(new_theta)
        self.y = r * math.sin(new_theta)

    # class methods -------------------------------
    def add(v, u):
        return PVector(v.x + u.x, v.y + u.y)

    def sub(v, u):
        return PVector(v.x - u.x, v.y - u.y)

    def mult(v, scalar):
        return PVector(v.x * scalar, v.y * scalar)

    def div(v, scalar):
        return PVector(v.x / scalar, v.y / scalar)

    def normalize(v):
        m = v.mag()
        if m == 0:
            return PVector(0,0)
        else:
            return PVector.div(v,m)

    def random2D():
        return PVector(uniform(-1,1), uniform(-1,1)).normalize()

    def dist(a, b):
        m = b.x - a.x
        n = b.y - a.y
        return math.sqrt(m ** 2 + n ** 2)


