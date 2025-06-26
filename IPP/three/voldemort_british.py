import sys
from itertools import permutations
from collections import Counter
import load_dictionary

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
    """Map letters in words to consonants & vowels"""
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
    n = int(total * target)
    count_pruned = Counter(cv_mapped_words).most_common(total - n)
    filtered_cv_map = set()
    for pattern, count in count_pruned:
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

def trigram_filter(word, list_):
    pass

def letter_pair_filter(list_):
    pass

def view_by_letter(word, list_):
    pass

if __name__ == '__main__':
    main()
