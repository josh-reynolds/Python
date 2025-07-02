"""Use dictionaries to look up number of syllables in a given word/phrase."""
import sys
from string import punctuation
import json
from nltk.corpus import cmudict

with open('missing_words.json', 'r', encoding='utf-8') as file:
    missing_words = json.load(file)

cmudict = cmudict.dict()

def count_syllables(words):
    """Use corpora to count syllables in English word or phrase."""
    words = words.replace('-', ' ')
    words = words.lower().split()
    num_sylls = 0
    for word in words:
        word = word.strip(punctuation)
        curly = chr(8217)   # curly quote not available on my keyboard
        if word.endswith("'s") or word.endswith(curly + "s"):
            word = word[:-2]
        if word in missing_words:
            num_sylls += missing_words[word]
        else:
            for phonemes in cmudict[word][0]:
                for phoneme in phonemes:
                    if phoneme[-1].isdigit():
                        num_sylls += 1
    return num_sylls

def main():
    """Take user input and print number of syllables in it."""
    while True:
        print("Syllable Counter")
        word = input("Enter word or phrase; else press Enter to Exit: ")
        if word == '':
            sys.exit()
        try:
            num_syllables = count_syllables(word)
            print(f"number of syllables in {word} is: {num_syllables}")
            print()
        except KeyError:
            pr_red("Word not found. Try again\n")

def pr_red(output):
    """Print string to console, colored red."""
    print(f"\033[91m{output}\033[00m")

if __name__ == '__main__':
    main()
