"""Chapter 7 - Complex Numbers."""
from math import sqrt
from engine import run
from screen_matrix import push_matrix, pop_matrix, translate, rect
# pylint: disable=C0103

WIDTH = 600
HEIGHT = 600
TITLE = "Complex Numbers"

xmin = -2
xmax = 2

ymin = -2
ymax = 2

rangex = xmax - xmin
rangey = ymax - ymin

xscl = float(rangex)/WIDTH
yscl = float(rangey)/HEIGHT

class ComplexNumber:
    """Representation and operations on a complex number."""

    def __init__(self, real, imaginary):
        """Create a complex number with real and imaginary parts."""
        self.r = real
        self.i = imaginary

    def __repr__(self):
        """Return string representation of a complex number."""
        if self.i < 0:
            sign = '-'
        else:
            sign = '+'
        return f"{self.r} {sign} {self.i}i"

    def magnitude(self):
        """Return magnitude of a complex number."""
        return sqrt(self.r**2 + self.i**2)

    @classmethod
    def mult(cls, left, right):
        """Multiplies two complex numbers."""
        return ComplexNumber(left.r * right.r - left.i * right.i,
                             left.i * right.r + left.r * right.i)

    @classmethod
    def add(cls, left,right):
        """Add two complex numbers."""
        return ComplexNumber(left.r + right.r,
                             left.i + right.i)

def mandelbrot(z, num):
    """Run the process num times and return the diverge count."""
    count = 0
    z1 = z
    while count <= num:
        if z1.magnitude() > 2.0:
            return count
        z1 = ComplexNumber.add(ComplexNumber.mult(z1, z1), z)
        count += 1
    return num

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    push_matrix()
    #translate(WIDTH/2, HEIGHT/2)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            z = ComplexNumber((xmin + x * xscl),
                              (ymin + y * yscl))
            col = mandelbrot(z,100)
            color = (255,255,255)
            if col == 100:
                color = (0,0,0)
            rect(x, y, 1, 1, color)

    pop_matrix()

run()
