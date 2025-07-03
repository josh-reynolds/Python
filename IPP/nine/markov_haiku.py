"""Create haiku by applying a Markov chain to a corpus of haikus."""
#import sys
import logging
#import random
from collections import defaultdict
#from count_syllables import count_syllables

#logging.disable(logging.CRITICAL)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def load_training_file(file):
    """Return text file as a string."""
    with open(file, 'r', encoding='utf-8') as in_file:
        raw_haiku = in_file.read()
        return raw_haiku

def prep_training(raw_haiku):
    """Load string, remove newline, split words on spaces and return list."""
    corpus = raw_haiku.replace('\n', ' ').split()
    return corpus

def map_word_to_word(corpus):
    """Load list and use dictionary to map word to word that follows."""
    limit = len(corpus) - 1
    dict1_to_1 = defaultdict(list)
    for index, word in enumerate(corpus):
        if index < limit:
            suffix = corpus[index + 1]
            dict1_to_1[word].append(suffix)
    logging.debug('map_word_to_word results for \"sake\" = %s\n',
                  dict1_to_1['sake'])
    return dict1_to_1

def map_2_words_to_word(corpus):
    """Load list and use dictionary to map word-pair to trailing word."""
    limit = len(corpus) - 2
    dict2_to_1 = defaultdict(list)
    for index, word in enumerate(corpus):
        if index < limit:
            key = word + ' ' + corpus[index + 1]
            suffix = corpus[index + 2]
            dict2_to_1[key].append(suffix)
    logging.debug('map_2_words_to_word results for \"sake jug\" = %s\n',
                  dict2_to_1['sake jug'])
    return dict2_to_1

def main():
    """Generate haiku using a Markov chain."""
    corpus = prep_training(load_training_file('train.txt'))
    map_word_to_word(corpus)
    map_2_words_to_word(corpus)

if __name__ == '__main__':
    main()
