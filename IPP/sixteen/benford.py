"""Assess a set of data for potential fraud using Benford's Law."""
#import sys
#import math
#from collections import defaultdict
#import matplotlib.pyplot as plt

BENFORD = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

def load_data(filename):
    """Open a text file & return a list of strings."""
    with open(filename, 'r', encoding='utf-8') as in_file:
        return in_file.read().strip().split('\n')
