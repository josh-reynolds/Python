"""Solve first-order equations."""
# pylint: disable=C0103

def equation(a,b,c,d):
    """Solve equations of the form ax + b = cx + d."""
    return (d - b)/(a - c)

print(f"The solution for 2x + 5 = 13 is {equation(2,5,0,13)}")
print(f"The solution for 12x + 18 = -34x + 67 is {equation(12,18,-34,67)}")
