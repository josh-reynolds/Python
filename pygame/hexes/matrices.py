# to run tests: python -m unittest -v matrices

import unittest
import tuples
import utils

class Matrix():
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.data = [[0 for x in range(columns)] for x in range(rows)]

    def transpose(self):
        result = matrix()
        for row in range(self.rows):
            for col in range(self.columns):
                result.data[col][row] = self.data[row][col]
        return result

    def determinant(self):
        result = 0 

        if self.rows == 2 and self.columns == 2:
            a,b = self.data[0]
            c,d = self.data[1]
            result = a * d - b * c
        else:
            for col in range(self.columns):
                result += self.data[0][col] * self.cofactor(0, col)

        return result

    def submatrix(self, row, column):
        result = matrix(self.rows-1, self.columns-1)
        for r in range(self.rows):
            trimmed_row = self.data[r].copy()  # need copy or we alias and mutate self
            trimmed_row.pop(column)
            if r < row:
                result.data[r] = trimmed_row
            if r == row:
                continue
            if r > row:
                result.data[r-1] = trimmed_row
        return result

    def minor(self, row, column):
        sub = self.submatrix(row, column)
        return sub.determinant()

    def cofactor(self, row, column):
        sign = -1
        if (row + column) % 2 == 0:
            sign = 1

        return self.minor(row, column) * sign

    def isInvertible(self):
        return self.determinant() != 0

    def inverse(self):
        if self.isInvertible():
            result = matrix(self.rows, self.columns)
            d = self.determinant()

            for row in range(self.rows):
                for col in range(self.columns):
                    c = self.cofactor(row, col)
                    result.data[col][row] = c/d  # col/row transposes matrix, which is what we want

            return result


    def __eq__(self, other):
        result = True
        if (isinstance(other, self.__class__) and
                self.rows == other.rows and
                self.columns == other.columns):
                    for row in range(self.rows):
                        for col in range(self.columns):
                            if not utils.flequal(self.__getitem__((row,col)), other[row,col]):
                                result = False
        else:
            result = False
        return result

    def __ne__(self, other):
        return not self.__eq__(other)

    def __mul__(self, rhs):         
        if isinstance(rhs, Matrix):      # only concerned with two 4x4 matrices here
            m = matrix()
            for row in range(self.rows):
                for col in range(self.columns):
                    m.data[row][col] = (self.data[row][0] * rhs[0, col] +
                                        self.data[row][1] * rhs[1, col] +
                                        self.data[row][2] * rhs[2, col] +
                                        self.data[row][3] * rhs[3, col])
            return m
        elif isinstance(rhs, tuples.Tuple):
            result = tuples.Tuple(0, 0, 0, 0)

            r1 = self.data[0]
            row1 = tuples.Tuple(r1[0], r1[1], r1[2], r1[3])
            result.x = row1.dot(rhs)

            r2 = self.data[1]
            row2 = tuples.Tuple(r2[0], r2[1], r2[2], r2[3])
            result.y = row2.dot(rhs)

            r3 = self.data[2]
            row3 = tuples.Tuple(r3[0], r3[1], r3[2], r3[3])
            result.z = row3.dot(rhs)

            r4 = self.data[3]
            row4 = tuples.Tuple(r4[0], r4[1], r4[2], r4[3])
            result.w = row4.dot(rhs)

            return result

    def __rmul__(self, lhs):
        return self.__mul__(lhs)

    def __getitem__(self, w):
        return self.data[w[0]][w[1]]

    def __str__(self):
        result = ""
        for x in range(self.rows):
            result += "| "
            for y in range(self.columns):
                result += str(self.data[x][y]) + " |"
            result += "\n"
        return result

def matrix(rows=4, columns=4):
    return Matrix(rows, columns)

def identity():
    result = matrix()
    result.data[0] = [1, 0, 0, 0]
    result.data[1] = [0, 1, 0, 0]
    result.data[2] = [0, 0, 1, 0]
    result.data[3] = [0, 0, 0, 1]
    return result

class MatrixTestCase(unittest.TestCase):
    def test_matrix_creation(self):
        m = matrix()
        m.data[0] = [   1,      2,     3,     4]
        m.data[1] = [ 5.5,    6.5,   7.5,   8.5]
        m.data[2] = [   9,     10,    11,    12]
        m.data[3] = [13.5,   14.5,  15.5,  16.5]

        self.assertEqual(m.data[0][0],    1)
        self.assertEqual(m.data[0][3],    4)
        self.assertEqual(m.data[1][0],  5.5)
        self.assertEqual(m.data[1][2],  7.5)
        self.assertEqual(m.data[2][2],   11)
        self.assertEqual(m.data[3][0], 13.5)
        self.assertEqual(m.data[3][2], 15.5)

    def test_matrix_access(self):
        m = matrix()
        m.data[0] = [   1,      2,     3,     4]
        m.data[1] = [ 5.5,    6.5,   7.5,   8.5]
        m.data[2] = [   9,     10,    11,    12]
        m.data[3] = [13.5,   14.5,  15.5,  16.5]

        self.assertEqual(m[0,0],    1)
        self.assertEqual(m[0,3],    4)
        self.assertEqual(m[1,0],  5.5)
        self.assertEqual(m[1,2],  7.5)
        self.assertEqual(m[2,2],   11)
        self.assertEqual(m[3,0], 13.5)
        self.assertEqual(m[3,2], 15.5)

    def test_creation_2_by_2_matrix(self):
        m = matrix(2,2)
        m.data[0] = [-3,  5]
        m.data[1] = [ 1, -2]

        self.assertEqual(m[0,0], -3)
        self.assertEqual(m[0,1],  5)
        self.assertEqual(m[1,0],  1)
        self.assertEqual(m[1,1], -2)
        
    def test_creation_3_by_3_matrix(self):
        m = matrix(3,3)
        m.data[0] = [-3,  5,  0]
        m.data[1] = [ 1, -2, -7]
        m.data[2] = [ 0,  1,  1]

        self.assertEqual(m[0,0], -3)
        self.assertEqual(m[1,1], -2)
        self.assertEqual(m[2,2],  1)

    def test_matrix_equality_with_identical_matrices(self):
        a = matrix()
        a.data[0] = [1, 2, 3, 4]
        a.data[1] = [5, 6, 7, 8]
        a.data[2] = [9, 8, 7, 6]
        a.data[3] = [5, 4, 3, 2]

        b = matrix()
        b.data[0] = [1, 2, 3, 4]
        b.data[1] = [5, 6, 7, 8]
        b.data[2] = [9, 8, 7, 6]
        b.data[3] = [5, 4, 3, 2]

        self.assertEqual(a, b)

    def test_matrix_equality_with_different_matrices(self):
        a = matrix()
        a.data[0] = [1, 2, 3, 4]
        a.data[1] = [5, 6, 7, 8]
        a.data[2] = [9, 8, 7, 6]
        a.data[3] = [5, 4, 3, 2]

        b = matrix()
        b.data[0] = [2, 3, 4, 5]
        b.data[1] = [6, 7, 8, 9]
        b.data[2] = [8, 7, 6, 5]
        b.data[3] = [4, 3, 2, 1]

        self.assertNotEqual(a, b)

    def test_matrix_equality_with_different_size_matrices(self):
        a = matrix()
        a.data[0] = [1, 2, 3, 4]
        a.data[1] = [5, 6, 7, 8]
        a.data[2] = [9, 8, 7, 6]
        a.data[3] = [5, 4, 3, 2]

        b = matrix(3,3)
        b.data[0] = [1, 2, 3]
        b.data[1] = [5, 6, 7]
        b.data[2] = [9, 8, 7]
        
        self.assertNotEqual(a, b)

    def test_multiplying_two_matrices(self):
        a = matrix()
        a.data[0] = [1, 2, 3, 4]
        a.data[1] = [5, 6, 7, 8]
        a.data[2] = [9, 8, 7, 6]
        a.data[3] = [5, 4, 3, 2]

        b = matrix()
        b.data[0] = [-2, 1, 2,  3]
        b.data[1] = [ 3, 2, 1, -1]
        b.data[2] = [ 4, 3, 6,  5]
        b.data[3] = [ 1, 2, 7,  8]

        result = matrix()
        result.data[0] = [20, 22,  50,  48]
        result.data[1] = [44, 54, 114, 108]
        result.data[2] = [40, 58, 110, 102]
        result.data[3] = [16, 26,  46,  42]

        self.assertEqual(a * b, result)

    def test_multiplying_matrix_by_tuple(self):
        a = matrix()
        a.data[0] = [1, 2, 3, 4]
        a.data[1] = [2, 4, 4, 2]
        a.data[2] = [8, 6, 4, 1]
        a.data[3] = [0, 0, 0, 1]

        b = tuples.Tuple(1, 2, 3, 1)

        self.assertEqual(a * b, tuples.Tuple(18, 24, 33, 1))

    def test_multiplying_matrix_by_identity(self):
        a = matrix()
        a.data[0] = [0, 1,  2,  4]
        a.data[1] = [1, 2,  4,  8]
        a.data[2] = [2, 4,  8, 16]
        a.data[3] = [4, 8, 16, 32]

        self.assertEqual(a * identity(), a)

    def test_multiplying_tuple_by_identity(self):
        a = tuples.Tuple(1, 2, 3, 4)

        self.assertEqual(identity() * a, a)

    def test_transposing_a_matrix(self):
        a = matrix()
        a.data[0] = [0, 9, 3, 0]
        a.data[1] = [9, 8, 0, 8]
        a.data[2] = [1, 8, 5, 3]
        a.data[3] = [0, 0, 5, 8]

        result = matrix()
        result.data[0] = [0, 9, 1, 0]
        result.data[1] = [9, 8, 8, 0]
        result.data[2] = [3, 0, 5, 5]
        result.data[3] = [0, 8, 3, 8]

        self.assertEqual(a.transpose(), result)

    def test_transposing_identity(self):
        a = identity().transpose()

        self.assertEqual(a, identity())

    def test_determinant_of_2_by_2_matrix(self):
        a = matrix(2, 2)
        a.data[0] = [ 1, 5]
        a.data[1] = [-3, 2]

        self.assertEqual(a.determinant(), 17)

    def test_submatrix_of_3_by_3_matrix(self):
        a = matrix(3, 3)
        a.data[0] = [ 1, 5,  0]
        a.data[1] = [-3, 2,  7]
        a.data[2] = [ 0, 6, -3]

        b = matrix(3, 3)
        b.data[0] = [ 1, 5,  0]
        b.data[1] = [-3, 2,  7]
        b.data[2] = [ 0, 6, -3]
        
        result = matrix(2, 2)
        result.data[0] = [-3, 2]
        result.data[1] = [ 0, 6]

        self.assertEqual(a.submatrix(0,2), result)
        self.assertEqual(a, b)   # verifying original matrix is not modified

    def test_submatrix_of_4_by_4_matrix(self):
        a = matrix()
        a.data[0] = [-6, 1,  1, 6]
        a.data[1] = [-8, 5,  8, 6]
        a.data[2] = [-1, 0,  8, 2]
        a.data[3] = [-7, 1, -1, 1]

        b = matrix()
        b.data[0] = [-6, 1,  1, 6]
        b.data[1] = [-8, 5,  8, 6]
        b.data[2] = [-1, 0,  8, 2]
        b.data[3] = [-7, 1, -1, 1]
        
        result = matrix(3, 3)
        result.data[0] = [-6,  1, 6]
        result.data[1] = [-8,  8, 6]
        result.data[2] = [-7, -1, 1]

        self.assertEqual(a.submatrix(2,1), result)
        self.assertEqual(a, b)   # verifying original matrix is not modified

    def test_calculating_minor_of_3_by_3_matrix(self):
        a = matrix(3,3)
        a.data[0] = [3,  5,  0]
        a.data[1] = [2, -1, -7]
        a.data[2] = [6, -1,  5]

        b = a.submatrix(1, 0)
        
        self.assertEqual(b.determinant(), 25)
        self.assertEqual(a.minor(1, 0), 25)

    def test_calculating_cofactor_of_3_by_3_matrix(self):
        a = matrix(3,3)
        a.data[0] = [3,  5,  0]
        a.data[1] = [2, -1, -7]
        a.data[2] = [6, -1,  5]

        self.assertEqual(a.minor(0,0), -12)
        self.assertEqual(a.cofactor(0,0), -12)

        self.assertEqual(a.minor(1,0), 25)
        self.assertEqual(a.cofactor(1,0), -25)

    def test_calculating_determinant_of_3_by_3_matrix(self):
        a = matrix(3,3)
        a.data[0] = [ 1, 2,  6]
        a.data[1] = [-5, 8, -4]
        a.data[2] = [ 2, 6,  4]

        self.assertEqual(a.cofactor(0,0),  56)
        self.assertEqual(a.cofactor(0,1),  12)
        self.assertEqual(a.cofactor(0,2), -46)
        self.assertEqual(a.determinant(), -196)

    def test_calculating_determinant_of_4_by_4_matrix(self):
        a = matrix()
        a.data[0] = [-2, -8,  3,  5]
        a.data[1] = [-3,  1,  7,  3]
        a.data[2] = [ 1,  2, -9,  6]
        a.data[3] = [-6,  7,  7, -9]

        self.assertEqual(a.cofactor(0,0),   690)
        self.assertEqual(a.cofactor(0,1),   447)
        self.assertEqual(a.cofactor(0,2),   210)
        self.assertEqual(a.cofactor(0,3),    51)
        self.assertEqual(a.determinant(), -4071)

    def test_invertible_matrix_for_invertibility(self):
        a = matrix()
        a.data[0] = [ 6,  4,  4,  4]
        a.data[1] = [ 5,  5,  7,  6]
        a.data[2] = [ 4, -9,  3, -7]
        a.data[3] = [ 9,  1,  7, -6]

        self.assertEqual(a.determinant(), -2120)
        self.assertTrue(a.isInvertible())

    def test_noninvertible_matrix_for_invertibility(self):
        a = matrix()
        a.data[0] = [-4,  2, -2, -3]
        a.data[1] = [ 9,  6,  2,  6]
        a.data[2] = [ 0, -5,  1, -5]
        a.data[3] = [ 0,  0,  0,  0]

        self.assertEqual(a.determinant(), 0)
        self.assertFalse(a.isInvertible())

    def test_calculating_inverse_of_a_matrix(self):
        a = matrix()
        a.data[0] = [-5,  2,  6, -8]
        a.data[1] = [ 1, -5,  1,  8]
        a.data[2] = [ 7,  7, -6, -7]
        a.data[3] = [ 1, -3,  7,  4]

        b = a.inverse()

        self.assertEqual(a.determinant(), 532)

        self.assertEqual(a.cofactor(2, 3), -160)
        self.assertEqual(b[3,2], -160 / 532)

        self.assertEqual(a.cofactor(3, 2), 105)
        self.assertEqual(b[2,3], 105 / 532)

        result = matrix()
        result.data[0] = [ 0.21805,  0.45113,  0.24060, -0.04511]
        result.data[1] = [-0.80827, -1.45677, -0.44361,  0.52068]
        result.data[2] = [-0.07895, -0.22368, -0.05263,  0.19737]
        result.data[3] = [-0.52256, -0.81391, -0.30075,  0.30639]

        self.assertEqual(b, result)

    def test_calculating_inverse_of_another_matrix(self):
        a = matrix()
        a.data[0] = [ 8, -5,  9,  2]
        a.data[1] = [ 7,  5,  6,  1]
        a.data[2] = [-6,  0,  9,  6]
        a.data[3] = [-3,  0, -9, -4]

        b = a.inverse()

        result = matrix()
        result.data[0] = [-0.15385, -0.15385, -0.28205, -0.53846]
        result.data[1] = [-0.07692,  0.12308,  0.02564,  0.03077]
        result.data[2] = [ 0.35897,  0.35897,  0.43590,  0.92308]
        result.data[3] = [-0.69231, -0.69231, -0.76923, -1.92308]

        self.assertEqual(b, result)

    def test_calculating_inverse_of_a_third_matrix(self):
        a = matrix()
        a.data[0] = [ 9,  3,  0,  9]
        a.data[1] = [-5, -2, -6, -3]
        a.data[2] = [-4,  9,  6,  4]
        a.data[3] = [-7,  6,  6,  2]

        b = a.inverse()

        result = matrix()
        result.data[0] = [-0.04074, -0.07778,  0.14444, -0.22222]
        result.data[1] = [-0.07778,  0.03333,  0.36667, -0.33333]
        result.data[2] = [-0.02901, -0.14630, -0.10926,  0.12963]
        result.data[3] = [ 0.17778,  0.06667, -0.26667,  0.33333]

        self.assertEqual(b, result)

    def test_multiplying_a_product_by_its_inverse(self):
        a = matrix()
        a.data[0] = [ 3, -9,  7,  3]
        a.data[1] = [ 3, -8,  2, -9]
        a.data[2] = [-4,  4,  4,  1]
        a.data[3] = [-6,  5, -1,  1]

        b = matrix()
        b.data[0] = [ 8,  2,  2,  2]
        b.data[1] = [ 3, -1,  7,  0]
        b.data[2] = [ 7,  0,  5,  4]
        b.data[3] = [ 6, -2,  0,  5]

        c = a * b

        self.assertEqual(c * b.inverse(), a)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
