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

def prep_words(word, list_):
    pass

def cv_map_words(list_):
    pass

def cv_map_filter(word, map_):
    pass

def trigram_filter(word, list_):
    pass

def letter_pair_filter(list_):
    pass

def view_by_letter(word, list_):
    pass

if __name__ == '__main__':
    main()
