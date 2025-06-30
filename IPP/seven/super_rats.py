import time
import random
import statistics

GOAL = 50000
NUM_RATS = 20
INITIAL_MIN_WT = 200
INITIAL_MAX_WT = 600
INITIAL_MODE_WT = 300
MUTATE_ODDS = 0.01
MUTATE_MIN = 0.5
MUTATE_MAX = 1.2
LITTER_SIZE = 8
LITTERS_PER_YEAR = 10
GENERATION_LIMIT = 500

if NUM_RATS % 2 != 0:
    NUM_RATS += 1

def populate(num_rats, min_wt, mx_wt, mode_wt):
    """Initialize a population with a triangular distribution of weights."""
    return [int(random.triangular(min_wt, max_wt, mode_wt))
            for i in range(num_rats)]
