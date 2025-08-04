"""Calculating factorials with recursion."""

def factorial(number):
    """Return number! (the factorial of number)."""
    if number == 0:
        return 1
    return number * factorial(number-1)

for i in range(10):
    print(factorial(i))
