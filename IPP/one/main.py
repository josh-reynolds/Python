import sys
from random import choice

print("Welcome to the Psych 'Sidekick Name Picker.'\n")
print("A name just like Sean would pick for Gus:\n\n")

first = ('Baby Oil', 'Bad News', 'Big Burps', "Bill 'Beenie-Weenie'")

last = ('Appleyard', 'Bigmeat', 'Bloominshine', 'Boogerbottom', 'Breedslovetrout')

# function not present in the book project - see note below
def pr_red(s):
    print("\033[91m {}\033[00m".format(s))

while True:
    first_name = choice(first)
    last_name = choice(last)

    print("\n\n")
    #print(f"{first_name} {last_name}", file=sys.stderr)
    pr_red(f"{first_name} {last_name}")
    print("\n\n")

    try_again = input("\n\nTry again? (Press Enter else n to quit)\n")
    if try_again.lower() == 'n':
        break

input("\nPress Enter to exit.")

# The book project uses sys.stderr to color the output red, but this assumes
# the script is being run in IDLE. In my console, this does not provide any coloring
# (and obfuscates things by appearing as an error).
#
# There are some modules that wrap ANSI codes for this, but it's also possible to
# do it raw, so going to try that out.


