"""Generate list of words containing a null cipher encoding of a message."""
from random import randint
import string
import load_dictionary

# Write a short message that doesn't contain punctuation or numbers!
INPUT_MESSAGE = "Panel at east end of chapel slides"

MESSAGE = ''
for char in INPUT_MESSAGE:
    if char in string.ascii_letters:
        MESSAGE += char
print(MESSAGE, "\n")
MESSAGE = ''.join(MESSAGE.split())

word_list = load_dictionary.load('words.txt')

vocab_list = []
for letter in MESSAGE:
    size = randint(6,10)
    for word in word_list:
        if (len(word) == size and
            word[2].lower() == letter.lower() and
            word not in vocab_list):
            vocab_list.append(word)
            break

if len(vocab_list) < len(MESSAGE):
    print("Word list is too small. Try larger dictionary or shorter message!")
else:
    print("Vocabulary words for Unit 1: \n", *vocab_list, sep="\n")
