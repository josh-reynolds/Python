"""Chapter 9 - Building Objects with Classes."""
from engine import run
from screen_matrix import circle

WIDTH = 600
HEIGHT = 600
TITLE = "Objects"

def update():
    """Update the app state once per frame."""

def draw():
    """Draw to the window once per frame."""
    global xcor, ycor, xvel, yvel
    screen.fill((0,0,0))
    xcor += xvel
    ycor += yvel

    if xcor > WIDTH or xcor < 0:
        xvel = -xvel
    if ycor > HEIGHT or ycor < 0:
        yvel = -yvel

    circle(xcor, ycor, 10, (255,255,255), 0)

xcor = 300
ycor = 300
xvel = 1
yvel = 2

run()
