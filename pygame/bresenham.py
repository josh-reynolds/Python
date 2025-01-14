# Trying out Bresenham's algorithm - this version just prints the points between two 
# enpoints p1 & p2, but any desired function can be substituted for the print statements
# below

# Adapted from Graphics Gems Vol I.

# usage:
# >>> a = Point(0,0)
# >>> b = Point(4,3)
# >>> bresenham(a,b)
# 0,0
# 1,1
# 2,2
# 3,2
# 4,3

# ---------------------------------------------------------------

import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def bresenham(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    ax = 2 * abs(dx)
    ay = 2 * abs(dy)

    sx = math.copysign(1, dx)
    sy = math.copysign(1, dy)

    x = p1.x
    y = p1.y

    if ax > ay:          # x dominant
        d = ay - ax/2
        while True:
            print("{},{}".format(int(x),int(y)))
            if x == p2.x:
                return
            if d >= 0:
                y = y + sy
                d = d - ax
            x = x + sx
            d = d + ay
    else:                # y dominant
        d = ax - ay/2
        while True:
            print("{},{}".format(int(x),int(y)))
            if y == p2.y:
                return
            if d >= 0:
                x = x + sx
                d = d - ay
            y = y + sy
            d = d + ax


