"""Experiment with turtle graphics and basic programming concepts."""
import turtle as t
# pylint cannot examine C modules by default, and consequently
# throws errors for missing members in the turtle module - disabling
# pylint: disable=E1101

def square(sidelength=100):
    """Draw a square of specified size."""
    for _ in range(4):
        t.forward(sidelength)
        t.right(90)

def triangle(sidelength=100):
    """Draw a triangle of specified size."""
    for _ in range(3):
        t.forward(sidelength)
        t.right(120)

def polygon(sidelength=100, sides=4):
    """Draw a regular polygon of specified size."""
    for _ in range(sides):
        t.forward(sidelength)
        t.right(360/sides)

t.shape('turtle')
polygon(100,7)


# --------------------------------------------------------------------
t.mainloop()  # required for running in a script, otherwise the window
              # closes immediately - book omits this detail
