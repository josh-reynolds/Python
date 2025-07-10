"""Model retirement income using Monte Carlo simulation."""
import sys
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

print("\nNote: Input data should be in percent, not decimal!\n")
try:
    bonds = read_to_list('10-yr_TBond_returns_1926-2013_pct.txt')
    stocks = read_to_list('SP500_returns_1926-2013_pct.txt')
    blend_40_50_10 = read_to_list('S-B-C_blend_1926-2013_pct.txt')
    blend_50_50 = read_to_list('S-B_blend_1926-2013_pct.txt')
    infl_rate = read_to_list('annual_infl_rate_1926-2013_pct.txt')
except IOError as exception:
    print(f"{exception}. \nTerminating program.")
    sys.exit(1)

investment_type_args = {'bonds': bonds, 'stocks': stocks,
                        'sp_blend': blend_50_50, 'sbc_blend': blend_40_50_10}

print("   stocks = SP500")
print("    bonds = 10-yr Treasury Bond")
print(" sb_blend = 50% SP500 / 50% TBond")
print("sbc_blend = 40% SP500 / 50% TBond / 10% Cash")
print("Press ENTER to take default value shown in [brackets].\n")
