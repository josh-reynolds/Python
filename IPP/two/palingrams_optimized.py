"""Find all word-pair palingrams in a dictionary file."""
import time
import load_dictionary

start_time = time.time()
word_list = load_dictionary.load('words.txt')

def find_palingrams():
    """Find dictionary palingrams."""
    pali_list = []
    words = set(word_list)
    for word in words:
        end = len(word)
        rev_word = word[::-1]
        if end > 1:
            for i in range(end):
                if (word[i:] == rev_word[:end-i] and
                    rev_word[end-i:] in words):
                    pali_list.append((word, rev_word[end-i:]))
                if (word[:i] == rev_word[end-i:] and
                    rev_word[:end-i] in words):
                    pali_list.append((rev_word[:end-i], word))
    return pali_list

palingrams = find_palingrams()
palingrams_sorted = sorted(palingrams)

print(f"\nNumber of palingrams = {len(palingrams_sorted)}\n")
for first, second in palingrams_sorted:
    print(f"{first} {second}")

end_time = time.time()
print(f"Run time for this program was {end_time-start_time} seconds.")
