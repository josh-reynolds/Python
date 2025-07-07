import random

def user_prompt(prompt, default=None):
    """Allow use of default values in input."""
    prompt = f"{prompt} [{default}]"
    response = input(prompt)
    if not response and default:
        return default
    else:
        return response

num_runs = int(user_prompt("Input number of runs", "20000"))

