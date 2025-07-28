"""Chapter 7 - Complex Numbers."""
from math import sqrt
from engine import run

WIDTH = 600
HEIGHT = 600
TITLE = "Complex Numbers"

class ComplexNumber:
    """Representation and operations on a complex number."""

    def __init__(self, real, imaginary):
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

    def mult(left, right):
        """Multiplies two complex numbers."""
        return ComplexNumber(left.r * right.r - left.i * right.i,
                             left.i * right.r + left.r * right.i)

    def add(left,right):
        """Adds two complex numbers."""
        return ComplexNumber(left.r + right.r,
                             left.i + right.i)


def update():
    """Update app state once per frame."""

def draw():
    """Draw to window once per frame."""

a = ComplexNumber(1,2)
b = ComplexNumber(3,4)
c = ComplexNumber(0,1)
d = ComplexNumber(2,1)
print(a)
print(b)
print(c)
print(d)
print(ComplexNumber.add(a,b))
print(ComplexNumber.mult(a,b))
print(ComplexNumber.mult(b,c))
print(d.magnitude())



run()
