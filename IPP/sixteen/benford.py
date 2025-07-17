"""Assess a set of data for potential fraud using Benford's Law."""
import sys
import math
from collections import defaultdict
#import matplotlib.pyplot as plt

BENFORD = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m {string}\033[00m")

def load_data(filename):
    """Open a text file & return a list of strings."""
    with open(filename, 'r', encoding='utf-8') as in_file:
        return in_file.read().strip().split('\n')

def count_first_digits(data_list):
    """Count 1st digits in list of numbers; return counts & frequency."""
    first_digits = defaultdict(int)
    for sample in data_list:
        if sample == '':
            continue
        try:
            int(sample)
        except ValueError as err:
            pr_red(err)
            pr_red("Samples must be integers. Exiting.")
            sys.exit(1)
        first_digits[sample[0]] += 1
    data_count = [v for (k, v) in sorted(first_digits.items())]
    total_count = sum(data_count)
    data_pct = [(i / total_count) * 100 for i in data_count]
    return data_count, data_pct, total_count

def get_expected_counts(total_count):
    """Return expected Benford's law counts for a total sample count."""
    return [round(p * total_count/100) for p in BENFORD]

def chi_square_test(data_count, expected_counts):
    """Return boolean on chi-square test (8 deg. freedom & P-val 0.05)."""
    chi_square_stat = 0
    for data, expected in zip(data_count, expected_counts):
        chi_square = math.pow(data - expected, 2)
        chi_square_stat += chi_square / expected

    print(f"\nChi Squared Test Statistic = {chi_square_stat:.3f}")
    print("Critical value at a P-value o 0.05 is 15.51.")

    return chi_square_stat < 15.51
