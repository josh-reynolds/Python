"""Find all anagrams in a dictionary file for a given word."""
import sys
from collections import Counter
import load_dictionary

dict_file = load_dictionary.load("words.txt")
dict_file.append('a')
dict_file.append('I')
dict_file = sorted(dict_file)

ini_name = input("Enter a name: ")

def find_angrams(name, word_list):
    """Read name & dictionary file and display all anagrams IN name."""
    name_letter_map = Counter(name)
    anagrams = []
    for word in word_list:
        test = ''
        word_letter_map = Counter(word.lower())
        for letter in word:
            if word_letter_map[letter] <= name_letter_map[letter]:
                test += letter
        if Counter(test) == word_letter_map:
            anagrams.append(word)
    print(*anagrams, sep='\n')
    print()
    print(f"Remaining letters = {name}")
    print(f"Number of remaining letters = {len(name)}")
    print(f"Number of remaining (real word) anagrams = {len(anagrams)}")

def process_choice(name):
    """Check user choice for validity, return choice and leftover letters."""
    while True:
        choice = input('\nMake a choice else Enter to start over or # to end: ')
        if choice == '':
            main()
        elif chioce == '#':
            sys.exit()
        else:
            candidate = ''.join(choice.lower().split())
        left_over_list = list(name)
        for letter in candidate:
            if letter in left_over_list:
                left_over_list.remove(letter)
        if len(name) - len(left_over_list) == len(candidate):
            break
        else:
            print("Won't work! Make another choice!")  ### print red
    name = ''.join(left_over_list)
    return choice, name


anagram_list = []

while True:
    print(f"Input name = {ini_name}")
    name = ini_name.lower()
    print(f"Using name = {name}")

    name_count = Counter(name)
    for word in dict_file:
        word_count = Counter(word.lower())
        if word != name:
            if word_count == name_count:
                anagram_list.append(word)

    print()
    if len(anagram_list) == 0:
        print("You need a larger dictionary or a new name!")
    else:
        print("Anagrams =", *anagram_list, sep='\n')

    try_again = input("\n\nTry again? (Press Enter or 'n' to quit)\n")
    if try_again.lower() == 'n':
        break

    anagram_list = []
