"""Chapter 8 - Using Matrices for Computer Graphics."""


def add_matrices(a,b):
    """Adds two 2x2 matrices together."""
    C = [[a[0][0] + b[0][0], a[0][1] + b[0][1]],
         [a[1][0] + b[1][0], a[1][1] + b[1][1]]]
    return C

def mult_matrices(a,b):
    """Multiplies two matrices together."""
    m = len(a)
    n = len(b[0])
    new_matrix = []
    for i in range(m):
        row = []
        for j in range(n):
            sum1 = 0
            for k in range(len(b)):
                sum1 += a[i][k] * b[k][j]
            row.append(sum1)
        new_matrix.append(row)
    return new_matrix


A = [[2,3],[5,-8]]
B = [[1,-4],[8,-6]]
C = add_matrices(A,B)
print(C)

D = [[1,-2],[2,1]]
E = [[3,-4],[5,6]]
F = mult_matrices(E,D)
print(F)
