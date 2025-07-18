"""Experiment with turtle graphics and basic programming concepts."""
import turtle as t
# pylint cannot examine C modules by default, and consequently
# throws errors for missing members in the turtle module - disabling
# pylint: disable=E1101

t.forward(100)
t.shape('turtle')
t.right(45)
t.forward(150)

t.mainloop()  # required for running in a script, otherwise the window
              # closes immediately - book omits this detail
