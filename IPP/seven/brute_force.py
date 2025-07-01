"""Brute force approach to finding a combination sequence."""
import time
from itertools import product

start_time = time.time()

combo = (9, 9, 7, 6, 5, 4, 3)

for perm in product([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], repeat=len(combo)):
    if perm == combo:
        print(f"Cracked! {combo} {perm}")
        break

end_time = time.time()
print(f"\nRun time for this program was "
      f"{(end_time - start_time):0.03f} seconds")
