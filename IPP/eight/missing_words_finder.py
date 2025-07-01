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

def cmudict_missing(word_set):
    """Find and return words in word set missing from cmudict."""
    exceptions = set()
    for word in word_set:
        word = word.lower().strip(punctuation)
        curly = chr(8217)   # curly quote not available on my keyboard
        if word.endswith("'s") or word.endswith(curly + "s"):
            word = word[:-2]
        if word not in cmudict:
            exceptions.add(word)
    print("\nexceptions:")
    print(*exceptions, sep='\n')
    print(f"Number of unique words in haiku corpus = {len(word_set)}")
    print(f"Number of words in corpus not in cmudict = {len(exceptions)}")
    membership = (1 - (len(exceptions) / len(word_set))) * 100
    print(f"cmudict membership = {membership:0.1f}{'%'}")
    return exceptions

def make_exceptions_dict(words):
    """Return dictionary of words and syllable counts from a set of words."""

def save_exceptions(dictionary):
    """Save exceptions dictionary as a json file."""

if __name__ == "__main__":
    main()
