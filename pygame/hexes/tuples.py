# to run tests: python -m unittest -v tuples

import unittest
import math
import utils

class Tuple():
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    
    def isPoint(self):
        return self.w == 1.0

    def isVector(self):
        return self.w == 0.0

    def magnitude(self):
        return math.sqrt(self.x ** 2 +
                         self.y ** 2 +
                         self.z ** 2 +
                         self.w ** 2)

    def normalize(self):
        mag = self.magnitude()
        return Tuple(self.x/mag,
                     self.y/mag,
                     self.z/mag,
                     self.w/mag)

    def dot(self, other):
        return (self.x * other.x +
                self.y * other.y +
                self.z * other.z +
                self.w * other.w)

    def cross(self, other):
        return vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)

    def reflect(self, normal):
        return self - normal * 2 * self.dot(normal)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (utils.flequal(self.x, other.x) and
                    utils.flequal(self.y, other.y) and
                    utils.flequal(self.z, other.z) and
                    utils.flequal(self.w, other.w))
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        return Tuple(self.x + other.x,
                     self.y + other.y,
                     self.z + other.z,
                     self.w + other.w)

    def __sub__(self, other):
        return Tuple(self.x - other.x,
                     self.y - other.y,
                     self.z - other.z,
                     self.w - other.w)

    def __neg__(self):
        return Tuple(-self.x, -self.y, -self.z, -self.w)

    def __mul__(self, rhs):
        if isinstance(rhs, float) or isinstance(rhs, int):
            return Tuple(self.x * rhs, self.y * rhs, self.z * rhs, self.w * rhs)

    def __rmul__(self, lhs):
        return self.__mul__(lhs)

    def __truediv__(self, rhs):
        if isinstance(rhs, float) or isinstance(rhs, int):
            return Tuple(self.x / rhs, self.y / rhs, self.z / rhs, self.w / rhs)

    def __str__(self):
        return "(" + (str(self.x) + ", " +
                     str(self.y) + ", " +
                     str(self.z) + ", " +
                     str(self.w) + ")")

    def __repr__(self):
        return "Tuple({},{},{},{})".format(self.x, self.y, self.z, self.w)


def point(x, y, z):
    return Tuple(x, y, z, 1)

def vector(x, y, z):
    return Tuple(x, y, z, 0)

class TupleTestCase(unittest.TestCase):
    def test_tuple_with_w_1_is_point(self):
        a = Tuple(4.3, -4.2, 3.1, 1.0)
        self.assertEqual(a.x,  4.3)
        self.assertEqual(a.y, -4.2)
        self.assertEqual(a.z,  3.1)
        self.assertEqual(a.w,  1.0)
        self.assertTrue(a.isPoint())
        self.assertFalse(a.isVector())

    def test_tuple_with_w_0_is_vector(self):
        a = Tuple(4.3, -4.2, 3.1, 0.0)
        self.assertEqual(a.x,  4.3)
        self.assertEqual(a.y, -4.2)
        self.assertEqual(a.z,  3.1)
        self.assertEqual(a.w,  0.0)
        self.assertFalse(a.isPoint())
        self.assertTrue(a.isVector())

    def test_point_creates_tuples_with_w_1(self):
        a = point(4, -4, 3)
        self.assertTrue(a.isPoint())
        self.assertFalse(a.isVector())
        self.assertEqual(a, Tuple(4, -4, 3, 1))

    def test_vector_creates_tuples_with_w_0(self):
        a = vector(4, -4, 3)
        self.assertFalse(a.isPoint())
        self.assertTrue(a.isVector())
        self.assertEqual(a, Tuple(4, -4, 3, 0))

    def test_adding_two_tuples(self):
        a1 = Tuple(3, -2, 5, 1)
        a2 = Tuple(-2, 3, 1, 0)
        self.assertEqual(a1 + a2, Tuple(1, 1, 6, 1))
    
    def test_subtracting_two_points(self):
        p1 = point(3, 2, 1)
        p2 = point(5, 6, 7)
        self.assertEqual(p1 - p2, vector(-2, -4, -6))

    def test_subtracting_vector_from_point(self):
        p = point(3, 2, 1)
        v = vector(5, 6, 7)
        self.assertEqual(p - v, point(-2, -4, -6))
        
    def test_subtracting_two_vectors(self):
        v1 = vector(3, 2, 1)
        v2 = vector(5, 6, 7)
        self.assertEqual(v1 - v2, vector(-2, -4, -6))

    def test_subtracting_vector_from_zero_vector(self):
        zero = vector(0, 0, 0)
        v = vector(1, -2, 3)
        self.assertEqual(zero - v, vector(-1, 2, -3))

    def test_negating_a_tuple(self):
        a = Tuple(1, -2, 3, -4)
        self.assertEqual(-a, Tuple(-1, 2, -3, 4))

    def test_multiply_tuple_by_scalar(self):
        a = Tuple(1, -2, 3, -4)
        self.assertEqual(a * 3.5, Tuple(3.5, -7, 10.5, -14))

    def test_multiply_tuple_by_fraction(self):
        a = Tuple(1, -2, 3, -4)
        self.assertEqual(a * 0.5, Tuple(0.5, -1, 1.5, -2))

    def test_multiply_tuple_is_commutative(self):
        a = Tuple(1, -2, 3, -4)
        self.assertEqual(3.5 * a, Tuple(3.5, -7, 10.5, -14))

    def test_divide_tuple_by_scalar(self):
        a = Tuple(1, -2, 3, -4)
        self.assertEqual(a / 2, Tuple(0.5, -1, 1.5, -2))

    def test_computing_magnitude_of_vector_1_0_0(self):
        v = vector(1, 0, 0)
        self.assertEqual(v.magnitude(), 1)

    def test_computing_magnitude_of_vector_0_1_0(self):
        v = vector(0, 1, 0)
        self.assertEqual(v.magnitude(), 1)

    def test_computing_magnitude_of_vector_0_0_1(self):
        v = vector(0, 0, 1)
        self.assertEqual(v.magnitude(), 1)

    def test_computing_magnitude_of_vector_1_2_3(self):
        v = vector(1, 2, 3)
        self.assertEqual(v.magnitude(), math.sqrt(14))

    def test_computing_magnitude_of_vector_neg1_neg2_neg3(self):
        v = vector(-1, -2, -3)
        self.assertEqual(v.magnitude(), math.sqrt(14))

    def test_normalizing_vector_4_0_0_gives_vector_1_0_0(self):
        v = vector(4, 0, 0)
        self.assertEqual(v.normalize(), vector(1, 0, 0))

    def test_normalizing_vector_1_2_3(self):
        v = vector(1, 2, 3)
        self.assertEqual(v.normalize(), vector(0.26726, 0.53452, 0.80178))

    def test_magnitude_of_normalized_vector(self):
        v = vector(1, 2, 3)
        norm = v.normalize()
        self.assertEqual(norm.magnitude(), 1)

    def test_dot_product_of_two_tuples(self):
        a = vector(1, 2, 3)
        b = vector(2, 3, 4)
        self.assertEqual(a.dot(b), 20)

    def test_cross_product_of_two_vectors(self):
        a = vector(1, 2, 3)
        b = vector(2, 3, 4)
        self.assertEqual(a.cross(b), vector(-1, 2, -1))
        self.assertEqual(b.cross(a), vector(1, -2, 1))

    def test_reflecting_a_vector_approaching_at_45_degrees(self):
        v = vector(1, -1, 0)
        n = vector(0, 1, 0)

        r = v.reflect(n)

        self.assertEqual(r, vector(1, 1, 0))

    def test_reflecting_a_vector_off_slanted_surface(self):
        v = vector(0, -1, 0)
        n = vector(math.sqrt(2)/2, math.sqrt(2)/2, 0)

        r = v.reflect(n)

        self.assertEqual(r, vector(1, 0, 0))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
