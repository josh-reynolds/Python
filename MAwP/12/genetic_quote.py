"""Guess a quote using a genetic algorithm."""
import random

target = "I never go back on my word, because that is my Ninja way."
characters = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.',?!"

def make_list():
    """Returns a list of characters the same length as the target."""
    char_list = []
    for i in range(len(target)):
        char_list.append(random.choice(characters))
    return char_list

def score(a_list):
    """Return number of matches between a_list and the target."""
    matches = 0
    for i in range(len(a_list)):
        if a_list[i] == target[i]:
            matches += 1
    return matches

def to_string(a_list):
    """Convert a list into a string."""
    return ''.join(a_list)

def mutate(a_list):
    """Returns a_list with one letter changed."""
    new_list = list(a_list)
    new_letter = random.choice(characters)
    index = random.randint(0, len(target)-1)
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
    else:
        print(to_string(guess), guess_score, guesses)
        if guess_score == len(target):
            break
        else:
            best_list = list(guess)
            best_score = guess_score
