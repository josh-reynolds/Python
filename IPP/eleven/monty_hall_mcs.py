"""Run Monte Carlo simulation of Monty Hall door game."""
import random
# pylint: disable=C0103

def user_prompt(prompt, default=None):
    """Allow use of default values in input."""
    prompt = f"{prompt} [{default}]"
    response = input(prompt)
    if not response and default:
        return default
    return response

num_runs = int(user_prompt("Input number of runs", "20000"))

first_choice_wins = 0
pick_change_wins = 0
doors = ['a', 'b', 'c']

for i in range(num_runs):
    winner = random.choice(doors)
    pick = random.choice(doors)

    if pick == winner:
        first_choice_wins += 1
    else:
        pick_change_wins += 1

print(f"Wins with original pick = {first_choice_wins}")
print(f"Wins with changed pick = {pick_change_wins}")
print(f"Probability of winning with initial "
      f"guess: {first_choice_wins/num_runs:.2f}")
print(f"Probability of winning by switching: "
      f"{pick_change_wins/num_runs:.2f}")

input("\nPress Enter key to exit.")
