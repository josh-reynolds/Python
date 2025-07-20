"""Number guessing game."""
from random import randint

def number_game():
    """Play the guessing game."""
    number = randint(1, 100)

    print("I'm thinking of a number between 1 and 100.")
    guess = int(input("What's your guess? "))

    while guess:
        if number == guess:
            print(f"That's correct! The number was {number}")
            break
        if number > guess:
            print("Nope. Higher.")
        else:
            print("Nope. Lower.")

        guess = int(input("What's your guess? "))

def greet():
    """Greet the player."""
    name = input("What's your name? ")
    print(f"Hello, {name}")

greet()
number_game()
