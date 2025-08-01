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

def gauss(A):
    """Perform Gaussian elimination on a matrix."""
    m = len(A)
    n = len(A[0])
    for j,row in enumerate(A):
        if row[j] != 0:
            divisor = row[j]
            for i, term in enumerate(row):
                row[i] = term/divisor
        for i in range(m):
            if i != j:
                addinv = -1 * A[i][j]
                for ind in range(n):
                    A[i][ind] += addinv * A[j][ind]
    return A

A = [[2,3],[5,-8]]
B = [[1,-4],[8,-6]]
C = add_matrices(A,B)
print(C)

D = [[1,-2],[2,1]]
E = [[3,-4],[5,6]]
F = mult_matrices(E,D)
print(F)

divisor = 2
row = [1,2,3,4,5]
for i, term in enumerate(row):
    row[i] = term/divisor
print(row)

G = [[2,1,-1,8],
     [-3,-1,2,-1],
     [-2,1,2,-3]]
print(gauss(G))

H = [[2,-1,5,1,-3],
     [3,2,2,-6,-32],
     [1,3,3,-1,-47],
     [5,-2,-3,3,49]]
print(gauss(H))



