'''The first project from Impractical Python Projects, by Lee Vaughan'''

from random import choice

# function not present in the book project - see note below
def pr_red(string):
    '''Print string to console, colored red.'''

    print(f"\033[91m {string}\033[00m")

def main():
    '''Main program loop.'''

    print("Welcome to the Psych 'Sidekick Name Picker.'\n")
    print("A name just like Sean would pick for Gus:\n\n")

    first = ('Baby Oil', 'Bad News', 'Big Burps', "Bill 'Beenie-Weenie'",
             "Bob 'Stinkbug'", 'Bowel Noises', 'Boxelder', "Bud 'Lite'",
             'Butterbean', 'Buttermilk', 'Buttocks', 'Chad', 'Chesterfield',
             'Chewy', 'Chigger', 'Cinnabuns', 'Cleet', 'Cornbread', 
             'Crab Meat', 'Crapp', 'Dark Skies', 'Dennis Clawhammer', 'Dicman',
             'Elphonso', 'Fancypants', 'Figgs', 'Foncy', 'Gootsy', 
             'Greasy Jim', 'Huckleberry', 'Huggy', 'Ignatious', 'Jimbo', 
             "Joe 'Pottin Soil'", 'Johnny', 'Lemongrass', 'Lil Debil', 
             'Longbranch', '"Lunch Money"',)


    last = ('Appleyard', 'Bigmeat', 'Bloominshine', 'Boogerbottom',
            'Breedslovetrout', 'Butterbaugh', 'Clovenhoof', 'Clutterbuck', 
            'Cocktoasten', 'Endicott', 'Fewhairs', 'Gooberdapple', 
            'Goodensmith', 'Goodpasture', 'Guster', 'Henderson', 'Hooperbag',
            'Hoosenater', 'Hootkins', 'Jefferson', 'Jenkins', 
            'Jingley-Schmidt', 'Johnson')


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

if __name__ == "__main__":
    main()

# The book project uses sys.stderr to color the output red, but this assumes
# the script is being run in IDLE. In my console, this does not provide any
# coloring (and obfuscates things by appearing as an error).
#
# There are some modules that wrap ANSI codes for this, but it's also possible
# to do it raw, so going to try that out.
