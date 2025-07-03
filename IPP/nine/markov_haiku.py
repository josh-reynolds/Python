"""Create haiku by applying a Markov chain to a corpus of haikus."""
#import sys
import logging
#import random
#from collections import defaultdict
#from count_syllables import count_syllables

#logging.disable(logging.CRITICAL)
logging.basicConfig(level=logging.DEBUG, format='%(messages)s')

def load_training_file(file):
    """Return text file as a string."""
    with open(file, 'r', encoding='utf-8') as in_file:
        raw_haiku = in_file.read()
        return raw_haiku

def prep_training(raw_haiku):
    """Load string, remove newline, split words on spaces and return list."""
    corpus = raw_haiku.replace('\n', ' ').split()
    return corpus

def main():
    """Generate haiku using a Markov chain."""
    output = prep_training(load_training_file('train.txt'))
    logging.debug(*output)

if __name__ == '__main__':
    main()
