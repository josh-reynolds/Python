"""Experiment with turtle graphics and basic programming concepts."""
import turtle as t
# pylint cannot examine C modules by default, and consequently
# throws errors for missing members in the turtle module - disabling
# pylint: disable=E1101

def square():
    for i in range(4):
        t.forward(100)
        t.right(90)

t.shape('turtle')
t.speed(0)
for i in range(60):
    square()
    t.right(5)

t.mainloop()  # required for running in a script, otherwise the window
              # closes immediately - book omits this detail
