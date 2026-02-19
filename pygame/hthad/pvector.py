"""Contains PVector class to represent points & vectors."""

import math
from random import uniform

class PVector:
    """Represents either a point or a vector."""

    def __init__(self, x, y):
        """Create an instance of a PVector object."""
        self.x = x
        self.y = y

    # instance methods ----------------------------
    def __repr__(self):
        """Return the developer string representation of a PVector."""
        return f"({self.x}, {self.y})"

    def __hash__(self):
        """Return the hash value of a PVector."""
        return hash((self.x, self.y))

    def __add__(self, other):
        """Add another PVector to self."""
        self.x += other.x
        self.y += other.y

    def __sub__(self, other):
        """Subtract another PVector from self."""
        self.x -= other.x
        self.y -= other.y

    def __mul__(self, scalar):
        """Multiply self by a scalar value."""
        self.x *= scalar
        self.y *= scalar

    def __truediv__(self, scalar):
        """Divide self by a scalar value."""
        self.x /= scalar
        self.y /= scalar

    def __eq__(self, other):
        """Test whether other is equal to self."""
        return self.x == other.x and self.y == other.y

    def dot(self, other):
        """Calculate the dot product of another PVector with self."""
        return (self.x * other.x) + (self.y * other.y)

    def cross(self, other):
        """Calculate the cross product of another PVector with self."""
        return (self.x * other.y) - (self.y * other.x)

    def angle_between(self, other):
        """Calculate the angle between self and another PVector."""
        dot = self.dot(other)
        return math.acos(dot / (self.mag() * other.mag()))

    def mag(self):
        """Return the magnitude of self."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def limit(self, max_):
        """Limit the magnitude of self to the specified value."""
        m = self.mag()
        if m > max_:
            # pylint: disable=W0104
            # W0104: Statement seems to have no effect (pointless-statement)
            self / m
            self * max_

    def copy(self):
        """Return a copy of self."""
        return PVector(self.x, self.y)

    def heading(self):
        """Calculate the heading (in degrees) of self."""
        return math.degrees(math.atan2(self.y, self.x))

    def set_mag(self, m):
        """Set the magnitude of self to the specified value."""
        p = self.normalize()
        # pylint: disable=W0104
        # W0104: Statement seems to have no effect (pointless-statement)
        p * m
        self.x, self.y = p.x, p.y

    def rotate(self, degrees):
        """Rotate self by the specified number of degrees."""
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
        """Add two PVectors together."""
        return PVector(v.x + u.x, v.y + u.y)

    def sub(v, u):
        """Subtract one PVector from another."""
        return PVector(v.x - u.x, v.y - u.y)

    def mult(v, scalar):
        """Multiply a PVector by a scalar value."""
        return PVector(v.x * scalar, v.y * scalar)

    def div(v, scalar):
        """Divide a PVector by a scalar value."""
        return PVector(v.x / scalar, v.y / scalar)

    def normalize(v):
        """Return a PVector normalized to magnitude 1."""
        m = v.mag()
        if m == 0:
            return PVector(0,0)
        return PVector.div(v,m)

    def random2D():
        """Return a random normalized PVector."""
        return PVector(uniform(-1,1), uniform(-1,1)).normalize()

    def dist(a, b):
        """Return the distance between two PVectors."""
        m = b.x - a.x
        n = b.y - a.y
        return math.sqrt(m ** 2 + n ** 2)
