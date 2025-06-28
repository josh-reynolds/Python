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
    """Check that input columns and rows are valid vs. message length"""
    factors = []
    len_cipher = len(cipherlist)
    for i in range(2, len_cipher):   # range excludes 1-column ciphers
        if len_cipher % i == 0:
            factors.append(i)
    print(f"\nLength of cipher = {len_cipher}")
    print(f"Acceptable column/row values include: {factors}")
    print()
    if ROWS * COLS != len_cipher:
        pr_red("\nError - Input columns & rows not factors of length "
               "of cipher. Terminating program.")
        sys.exit(1)

def key_to_int(key):
    """Turn key into list of integers & check validity."""
    key_int = [int(i) for i in key.split()]
    key_int_lo = min(key_int)
    key_int_hi = max(key_int)
    if len(key_int) != COLS or key_int_lo < -COLS or key_int_hi > COLS \
            or 0 in key_int:
                pr_red("\nError - Problem with key. Terminating program.")
                sys.exit(1)
    else:
        return key_int

def build_matrix(key_int, cipherlist):
    """Turn every n items in a list into a new item in a list of lists."""
    translation_matrix = [None] * COLS
    start = 0
    stop = ROWS
    for k in key_int:
        if k < 0:    # read bottom-to-top of column
            col_items = cipherlist[start:stop]
        elif k > 0:
            col_items = list(reversed(cipherlist[start:stop]))
        translation_matrix[abs(k) - 1] = col_items
        start += ROWS
        stop += ROWS
    return translation_matrix

def decrypt(translation_matrix):
    pass

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m{string}\033[00m")

if __name__ == '__main__':
    main()
