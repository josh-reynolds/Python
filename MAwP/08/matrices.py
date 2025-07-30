"""Chapter 8 - Using Matrices for Computer Graphics."""

A = [[2,3],[5,-8]]
B = [[1,-4],[8,-6]]

def add_matrices(a,b):
    """Adds two 2x2 matrices together."""
    C = [[a[0][0] + b[0][0], a[0][1] + b[0][1]],
         [a[1][0] + b[1][0], a[1][1] + b[1][1]]]
    return C

C = add_matrices(A,B)
print(C)

