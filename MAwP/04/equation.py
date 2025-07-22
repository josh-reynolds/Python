"""Solve equations."""
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

def g(x):
    """Cubic equation."""
    return 6*x**3 + 31*x**2 + 3*x - 10

def plug():
    """Brute force test for solutions to a cubic equation."""
    x = -100
    solution = []
    while x < 100:
        if g(x) == 0:
            solution.append(x)
        x += 1
    return solution

def average(a,b):
    """Return average of a and b."""
    return (a + b)/2

def guess():
    """Find solution using binary search guesses."""
    lower = -1
    upper = 0
    for i in range(20):
        midpt = average(lower, upper)
        if g(midpt) == 0:
            return midpt
        elif g(midpt) < 0:
            upper = midpt
        else:
            lower = midpt
    return midpt

print(f"The solution for 2x + 5 = 13 is {equation(2,5,0,13)}")
print(f"The solution for 12x + 18 = -34x + 67 is {equation(12,18,-34,67)}")
print(f"The solutions for 2x^2 + 7x -15 = 0 are {quad(2,7,-15)}")
print(f"A solution for 6x^3 + 31x^2 + 3x - 10 = 0 is {plug()}")

result = guess()
print(f"{result} {g(result)}")
print(f"{g(-2/3)}")
