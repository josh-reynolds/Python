"""Calculate factors of a given number."""

def factors(num):
    """Return a list of the factors of num."""
    factor_list = []
    for i in range(1, num+1):
        if num % i == 0:
            factor_list.append(i)
    return factor_list

def gcf(num1, num2):
    """Find Greatest Common Factor of two munbers."""
    fact1 = factors(num1)
    fact2 = factors(num2)
    greatest = 0
    for num in fact1:
        if num in fact2 and num > greatest:
            greatest = num
    return greatest

print("Greatest Common Factor\n")
while True:
    number1 = input("Enter the first number (or 'q' to quit): ")
    if number1 == 'q':
        break

    number2 = input("Enter the second number (or 'q' to quit): ")
    if number2 == 'q':
        break

    great = gcf(int(number1), int(number2))
    print(f"The greatest common factor of {number1} and ",
          f"{number2} is {great}\n")
