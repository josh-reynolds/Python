"""Calculate factors of a given number."""

def factors(num):
    """Return a list of the factors of num."""
    factor_list = []
    for i in range(1, num+1):
        if num % i == 0:
            factor_list.append(i)
    return factor_list

while True:
    number = input("Enter a number (or 'q' to quit): ")
    if number == 'q':
        break
    fact = factors(int(number))
    print(f"The factors of {number} are:")
    print(fact)
