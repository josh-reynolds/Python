"""Find all anagrams in a dictionary file for a given word."""
from collections import Counter
import load_dictionary

word_list = load_dictionary.load("words.txt")
anagram_list = []

while True:
    name = input("Input a name.\n")
    print(f"Input name = {name}")
    name = name.lower()
    print(f"Using name = {name}")

    name_count = Counter(name)
    for word in word_list:
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
