"""Use a genetic algorithm to crack a combination."""
import time
from random import randint, randrange

def fitness(combo, attempt):
    """Compare items in two lists and count number of matches."""
    grade = 0
    for i, j in zip(combo, attempt):
        if i == j:
            grade += 1
    return grade

def main():
    """Use hill-climbing algorithm to solve lock combinations."""
    combination = '6822858902'
    print(f"Combination = {combination}")
    combo = [int(i) for i in combination]

    best_attempt = [0] * len(combo)
    best_attempt_grade = fitness(combo, best_attempt)

    count = 0

    while best_attempt != combo:
        next_try = best_attempt[:]

        lock_wheel = int(randrange(0, len(combo)))
        next_try[lock_wheel] = randint(0, len(combo)-1)

        next_try_grade = fitness(combo, next_try)
        if next_try_grade > best_attempt_grade:
            best_attempt = next_try[:]
            best_attempt_grade = next_try_grade
        print(next_try, best_attempt)
        count += 1

    print()
    print(f"Cracked! {best_attempt}", end=' ')
    print(f"in {count} tries")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nRun time for this program was {duration:0.5f} seconds.")
