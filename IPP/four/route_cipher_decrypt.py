"""Decrypt a paht through a Union Route Cipher.

Designed for whole-word transposition ciphers with variable rows and columns.
Assumes encryption began at either the top or bottom of a column.
Key indicates the order to read columns and the direction to traverse.
Negative column numbers mean start at bottom nd read up.
Positive column numbers mean start at top and read down.

Example below is for 4x4 matrix with key -1 2 -3 4.
Note "0" is not allowed.
Arrows show encryption route; for negative key values read UP.

  1   2   3   4
-----------------
| ^ | | | ^ | | | MESSAGE IS WRITTEN
| | | V | | | V |
-----------------
| ^ | | | ^ | | | ACROSS EACH ROW
| | | V | | | V |
-----------------
| ^ | | | ^ | | | IN THIS MANNER
| | | V | | | V |
-----------------
| ^ | | | ^ | | | LAST ROW IS FILLED WITH DUMMY WORDS
| | | V | | | V |
-----------------
START        END

Required inputs - a text message, # of columns, # of rows, key string

Prints translated plaintext
"""
import sys

# the string to be decrypted (type or paste between triple-quotes):
ciphertext = """16 12 8 4 0 1 5 9 13 17 18 14 10 6 2 3 7 11 15 19"""

# number of columns in the transposition matrix
COLS = 4

# number of rows in the transposition matrix
ROWS = 5

# key with spaces between numbers; negative to read UP column (ex = -1 2 -3 4):
key = """-1 2 -3 4"""

# END OF USER INPUT - DO NOT EDIT BELOW THIS LINE
# =============================================================================


def main():
    """Run program and print decrypted plaintext."""
    print(f"\nCiphertext = {ciphertext}")
    print(f"Trying {COLS} columns")
    print(f"Trying {ROWS} rows")
    print(f"Trying key = {key}")

    # split elements into words, not letters
    cipherlist = list(ciphertext.split())
    validate_col_row(cipherlist)
    key_int = key_to_int(key)
    translation_matrix = build_matrix(key_int, cipherlist)
    plaintext = decrypt(translation_matrix)

    print(f"Plaintext = {plaintext}")

def validate_col_row(cipherlist):
    pass

def key_to_int(key):
    pass

def build_matrix(key_int, cipherlist):
    pass

def decrypt(translation_matrix):
    pass

if __name__ == '__main__':
    main()
