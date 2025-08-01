"""Chapter 7 - Complex Numbers."""
from math import sqrt
import pygame
from engine import run, screen
# pylint: disable=C0103

WIDTH = 600
HEIGHT = 600
TITLE = "Complex Numbers"

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

def mandelbrot(value, num):
    """Run the process num times and return the diverge count."""
    count = 0
    z1 = value
    while count <= num:
        if z1.magnitude() > 2.0:
            return count
        z1 = ComplexNumber.add(ComplexNumber.mult(z1, z1), value)
        count += 1
    return num

def julia(value, c,num):
    """Run the process num times and return the diverge count."""
    count = 0
    z1 = value
    while count <= num:
        if z1.magnitude() > 2.0:
            return count
        z1 = ComplexNumber.add(ComplexNumber.mult(z1, z1), c)
        count += 1
    return num

def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""
    screen.blit(image, (0,0))

# ADJUST THESE VALUES TO ZOOM ------------------
xmin = -1.5
xmax = 1.5

ymin = -1.5
ymax = 1.5
# ---------------------------------------------
# Julia Set constant
constant = ComplexNumber(0.285, 0.01)
# ---------------------------------------------

rangex = xmax - xmin
rangey = ymax - ymin

xscl = float(rangex)/WIDTH
yscl = float(rangey)/HEIGHT

raster = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
color = pygame.Color(0,0,0)

#print("Calculating mandelbrot data")
print("Calculating julia data")
for x in range(WIDTH):
    for y in range(HEIGHT):
        z = ComplexNumber((xmin + x * xscl),
                          (ymin + y * yscl))
        #col = mandelbrot(z,100)
        col = julia(z,constant,100)
        raster[x][y] = col

print("Rendering to image")
image = pygame.Surface((WIDTH,HEIGHT))
for i in range(WIDTH):
    for j in range(HEIGHT):
        if raster[i][j] == 100:
            color = pygame.Color(0,0,0)
        else:
            color.hsva = (3*raster[i][j],100,100)
        pygame.draw.rect(image,color, (i, j, 1, 1))

run()
