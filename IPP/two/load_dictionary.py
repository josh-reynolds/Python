"""Load a text file as a list.

Arguments:
    - Text file name (and directory path, if needed).

Exceptions:
    - IOError if filename not found.

Returns:
    - A list of all words in a text file in lower case.

Requires-import sys
"""
import sys

def load(file):
    """Open a text file & return a list of lowercase strings."""
    try:
        with open(file, 'r', encoding='utf-8') as in_file:
            loaded_txt = in_file.read().strip().split('\n')
            loaded_txt = [x.lower() for x in loaded_txt]
            return loaded_txt
    except IOError as error:
        print(f"{error}\nError opening {file}. Terminating program.",
              file=sys.stderr)
        sys.exit(1)
