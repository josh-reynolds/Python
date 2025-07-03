"""Check corpus against syllable dictionaries to identify missing words."""
import count_syllables

def pr_red(output):
    """Print string to console, colored red."""
    print(f"\033[91m{output}\033[00m")

with open('train.txt', 'r', encoding='utf-8') as file:
    words = set(file.read().split())

missing = []

for word in words:
    try:
        num_syllables = count_syllables.count_syllables(word)
        #print(word, num_syllables, end='\n')
    except KeyError:
        missing.append(word)

pr_red("Missing words:")
for word in missing:
    pr_red(word)
