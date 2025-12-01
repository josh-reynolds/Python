"""Contains ANSI code constants for formatting output."""

# see wikipedia page for ANSI codes
HOME = "\033[H"
CLEAR = "\033[2J"
BOLD = "\033[1m"
YELLOW_ON_RED = "\033[1;33;41m"
BOLD_RED = "\033[1;31;40m"
BOLD_GREEN = "\033[1;32;40m"
BOLD_YELLOW = "\033[1;33;40m"
BOLD_BLUE = "\033[1;36;40m"
END_FORMAT = "\033[00m"

#string = "foo bar"
#start = 60 - (len(string)//2)
#print(f"\033[1;30;41m\033[{start}G{string}\033[00m")
#print(f"\033[1m{string}\033[00m")    # bold
#print(f"\033[2m{string}\033[00m")    # faint
#print(f"\033[3m{string}\033[00m")    # italic (same as inverse)
#print(f"\033[4m{string}\033[00m")    # underline
#print(f"\033[5m{string}\033[00m")    # slow blink
#print(f"\033[6m{string}\033[00m")    # fast blink (same as slow)
#print(f"\033[7m{string}\033[00m")    # inverse
#print(f"\033[8m{string}\033[00m")    # hide
#print(f"\033[9m{string}\033[00m")    # strikethrough
#print(f"\033[21m{string}\033[00m")   # dbl. underline (same as underline)
