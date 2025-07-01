"""Review CMUDICT for missing words."""
import sys
from string import punctuation
import pprint
import json
from nltk.corpus import cmudict

cmudict = cmudict.dict()   # Carnegie Mellon University Pronouncing Dictionary

def main():
    """Examine CMUDICT for missing words and build exception list."""
    haiku = load_haiku('train.txt')
    exceptions = cmudict_missing(haiku)
    build_dict = input("\nManually build an exceptions dictionary (y/n)?\n")
    if build_dict.lower() == 'n':
        sys.exit()
    else:
        missing_words_dict = make_exceptions_dict(exceptions)
        save_exceptions(missing_words_dict)

def load_haiku(filename):
    """Open and return training corpus of haiku as a set."""
    with open(filename) as in_file:
        haiku = set(in_file.read().replace('-', ' ').split())
        return haiku

def cmudict_missing(words):
    """Find and return words in word set missing from cmudict."""

def make_exceptions_dict(words):
    """Return dictionary of words and syllable counts from a set of words."""

def save_exceptions(dictionary):
    """Save exceptions dictionary as a json file."""

if __name__ == "__main__":
    main()
