"""Solve first-order equations."""
from math import sqrt
# pylint: disable=C0103

def equation(a,b,c,d):
    """Solve equations of the form ax + b = cx + d."""
    return (d - b)/(a - c)

def quad(a,b,c):
    """Solve quadratic equations (ax**2 + bx + c = 0)."""
    x1 = (-b + sqrt(b**2 - 4*a*c))/(2*a)
    x2 = (-b - sqrt(b**2 - 4*a*c))/(2*a)
    return x1, x2

print(f"The solution for 2x + 5 = 13 is {equation(2,5,0,13)}")
print(f"The solution for 12x + 18 = -34x + 67 is {equation(12,18,-34,67)}")
print(f"The solutions for 2x^2 + 7x -15 = 0 are {quad(2,7,-15)}")
