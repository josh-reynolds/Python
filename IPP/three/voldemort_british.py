"""Filter letter permutations to find anagrams of 'Voldemort'."""
import sys
from itertools import permutations
from collections import Counter
import load_dictionary

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m{string}\033[00m")

def main():
    """Load files, run filters, allow user to view anagrams by first letter."""
    name = 'tmvoordle'
    name = name.lower()

    word_list_ini = load_dictionary.load('words.txt')
    trigrams_filtered = load_dictionary.load('least-likely_trigrams.txt')

    word_list = prep_words(name, word_list_ini)
    filtered_cv_map = cv_map_words(word_list)
    filter_1 = cv_map_filter(name, filtered_cv_map)
    filter_2 = trigram_filter(filter_1, trigrams_filtered)
    filter_3 = letter_pair_filter(filter_2)
    view_by_letter(name, filter_3)

def prep_words(name, word_list_ini):
    """Prep word list for finding anagrams."""
    print(f"length initial word_list = {len(word_list_ini)}")
    len_name = len(name)
    word_list = [word.lower() for word in word_list_ini
                 if len(word) == len_name]
    print(f"length of new word_list = {len(word_list)}")
    return word_list

def cv_map_words(word_list):
    """Map letters in words to consonants & vowels."""
    vowels = 'aeiouy'
    cv_mapped_words = []
    for word in word_list:
        temp = ''
        for letter in word:
            if letter in vowels:
                temp += 'v'
            else:
                temp += 'c'
        cv_mapped_words.append(temp)

    total = len(set(cv_mapped_words))
    target = 0.05
    rejected_fraction = int(total * target)
    count_pruned = Counter(cv_mapped_words).most_common(total -
                                                        rejected_fraction)
    filtered_cv_map = set()
    for pattern, _ in count_pruned:
        filtered_cv_map.add(pattern)
    print(f"length filtered_cv_map = {len(filtered_cv_map)}")
    return filtered_cv_map

def cv_map_filter(name, filtered_cv_map):
    """Remove permutations of words based on unlikely cons-vowel combos."""
    perms = {''.join(i) for i in permutations(name)}
    print(f"length of initial permutations set = {len(perms)}")
    vowels = 'aeiouy'
    filter_1 = set()
    for candidate in perms:
        temp = ''
        for letter in candidate:
            if letter in vowels:
                temp += 'v'
            else:
                temp += 'c'
        if temp in filtered_cv_map:
            filter_1.add(candidate)
    print(f"# choices after filter_1 = {len(filter_1)}")
    return filter_1

def trigram_filter(filter_1, trigrams_filtered):
    """Remove unlikely trigrams from permutations."""
    filtered = set()
    for candidate in filter_1:
        for triplet in trigrams_filtered:
            triplet = triplet.lower()
            if triplet in candidate:
                filtered.add(candidate)
    filter_2 = filter_1 - filtered
    print(f"# choices after filter_2 = {len(filter_2)}")
    return filter_2

def letter_pair_filter(filter_2):
    """Remove unlikely letter-pairs from permutations."""
    filtered = set()
    rejects = ['dt', 'lr', 'md', 'ml', 'mr', 'mt', 'mv',
               'td', 'tv', 'vd', 'vl', 'vm', 'vr', 'vt']
    first_pair_rejects = ['ld', 'lm', 'lt', 'lv', 'rd',
                          'rl', 'rm', 'rt', 'rv', 'tl', 'tm']
    for candidate in filter_2:
        for reject in rejects:
            if reject in candidate:
                filtered.add(candidate)
        for firstpair in first_pair_rejects:
            if candidate.startswith(firstpair):
                filtered.add(candidate)
    filter_3 = filter_2 - filtered
    print(f"# choices after filter_3 = {len(filter_3)}")
    if 'voldemort' in filter_3:
        pr_red("Voldemort found!")
    return filter_3

def view_by_letter(name, filter_3):
    """Filter to aagrams starting with input letter."""
    print(f"Remaining letters = {name}")
    first = input("select a starting letter or press Enter to see all: ")
    subset = []
    for candidate in filter_3:
        if candidate.startswith(first):
            subset.append(candidate)
    print(*sorted(subset), sep='\n')
    print(f"Number of choices starting with {first} = {len(subset)}")
    try_again = input("Try again? (Press Enter else any other key to exit):")
    if try_again.lower() == '':
        view_by_letter(name, filter_3)
    else:
        sys.exit()

if __name__ == '__main__':
    main()
