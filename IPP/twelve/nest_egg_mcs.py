"""Model retirement income using Monte Carlo simulation."""
#import sys
#import random
#import matplotlib.pyplot as plt

def read_to_list(file_name):
    """Open a file of data in percent, convert to decimal & return a list."""
    with open(file_name, 'r', encoding='utf-8') as in_file:
        lines = [float(line.strip()) for line in in_file]
        decimal = [round(line / 100, 5) for line in lines]
        return decimal

def default_input(prompt, default=None):
    """Allow use of default values in input."""
    prompt = f"{prompt} [{default}]"
    response = input(prompt)
    if not response and default:
        return default
    return response
