"""Guess a quote using a genetic algorithm."""
import random
# pylint: disable=C0103

TARGET = "I never go back on my word, because that is my Ninja way."
CHARACTERS = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.',?!"

def make_list():
    """Return a list of CHARACTERS the same length as the TARGET."""
    char_list = []
    for _ in range(len(TARGET)):
        char_list.append(random.choice(CHARACTERS))
    return char_list

def score(a_list):
    """Return number of matches between a_list and the TARGET."""
    matches = 0
    for i, letter in enumerate(a_list):
    #for i in range(len(a_list)):
        if letter == TARGET[i]:
        #if a_list[i] == TARGET[i]:
            matches += 1
    return matches

def to_string(a_list):
    """Convert a list into a string."""
    return ''.join(a_list)

def mutate(a_list):
    """Return a_list with one letter changed."""
    new_list = list(a_list)
    new_letter = random.choice(CHARACTERS)
    index = random.randint(0, len(TARGET)-1)
    new_list[index] = new_letter
    return new_list

random.seed()
best_list = make_list()
best_score = score(best_list)
guesses = 0

while True:
    guess = mutate(best_list)
    guess_score = score(guess)
    guesses += 1
    if guess_score <= best_score:
        continue

    print(to_string(guess), guess_score, guesses)

    if guess_score == len(TARGET):
        break

    best_list = list(guess)
    best_score = guess_score
