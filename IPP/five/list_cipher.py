from random import randint
import string
import load_dictionary

# Write a short message that doesn't contain punctuation or numbers!
input_message = "Panel at east end of chapel slides"

message = ''
for char in input_message:
    if char in string.ascii_letters:
        message += char
print(message, "\n")
message = ''.join(message.split())
