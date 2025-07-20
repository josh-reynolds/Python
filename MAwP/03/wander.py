"""Random walk using turtle module."""
import turtle as t
from random import randint
# pylint: disable=E1101

t.speed(0)

def wander():
    """Turtle random walk in infinite loop."""
    while True:
        t.forward(3)
        if (t.xcor() >= 200 or t.xcor() <= -200 or
            t.ycor() >= 200 or t.ycor() <= -200):
            t.left(randint(90,180))

wander()
