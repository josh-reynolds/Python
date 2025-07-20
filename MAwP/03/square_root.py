"""Approximate square root of a number."""

def average(first, second):
    """Return the average of two numbers."""
    return (first + second)/2

def square_root(number, low, high):
    """Find the square root of number.

    Repeatedly guesses values and evaluates
    whether they are too high or too low.
    """
    for _ in range(20):
        guess = average(low, high)
        square_guess = guess**2
        if square_guess == number:
            print(guess)
        elif square_guess > number:
            high = guess
        else:
            low = guess
    return guess

print(f"The square root of 60 is {square_root(60, 7, 8)}")
print(f"The square root of 200 is {square_root(200, 10, 20)}")
print(f"The square root of 1000 is {square_root(1000, 20, 50)}")
print(f"The square root of 50000 is {square_root(50000, 1, 500)}")
