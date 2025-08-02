"""Chapter 9 - Building Objects with Classes."""
from random import randrange, randint
from engine import run
from screen_matrix import circle
# pylint: disable=C0103, W0603

WIDTH = 600
HEIGHT = 600
TITLE = "Objects"

class Ball:
    """Bouncing Ball object."""

    def __init__(self, x, y):
        """Create a Ball object."""
        self.xcor = x
        self.ycor = y
        self.xvel = randrange(-2,2)
        self.yvel = randrange(-2,2)
        self.color = (randint(0,255),
                      randint(0,255),
                      randint(0,255))
        self.radius = randint(3,25)

    def update(self):
        """Update Ball state."""
        self.xcor += self.xvel
        self.ycor += self.yvel
        if self.xcor > WIDTH or self.xcor < 0:
            self.xvel = -self.xvel
        if self.ycor > WIDTH or self.ycor < 0:
            self.yvel = -self.yvel

    def draw(self):
        """Draw a Ball at its position."""
        circle(self.xcor, self.ycor, self.radius, self.color, 0)

class Sheep:
    """Sheep object."""

    def __init__(self, x, y):
        """Create a Sheep object."""
        self.x = x
        self.y = y
        self.sz = 10

    def update(self):
        """Update Sheep state."""

    def draw(self):
        """Draw a Sheep at its position."""
        circle(self.x, self.y, self.sz, (0,0,0), 0)

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    shawn.draw()

shawn = Sheep(300,200)

run()
