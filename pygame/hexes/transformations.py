# to run tests: python -m unittest -v transformations

import unittest
import math
import tuples
import matrices

def translation(dx, dy, dz):
    result = matrices.identity()
    result.data[0][3] = dx
    result.data[1][3] = dy
    result.data[2][3] = dz
    return result

def scaling(dx, dy, dz):
    result = matrices.identity()
    result.data[0][0] = dx
    result.data[1][1] = dy
    result.data[2][2] = dz
    return result

def rotation_x(radians):
    result = matrices.identity()
    result.data[1][1] = math.cos(radians)
    result.data[1][2] = -math.sin(radians)
    result.data[2][1] = math.sin(radians)
    result.data[2][2] = math.cos(radians)
    return result

def rotation_y(radians):
    result = matrices.identity()
    result.data[0][0] = math.cos(radians)
    result.data[0][2] = math.sin(radians)
    result.data[2][0] = -math.sin(radians)
    result.data[2][2] = math.cos(radians)
    return result

def rotation_z(radians):
    result = matrices.identity()
    result.data[0][0] = math.cos(radians)
    result.data[0][1] = -math.sin(radians)
    result.data[1][0] = math.sin(radians)
    result.data[1][1] = math.cos(radians)
    return result

def shearing(xy, xz, yx, yz, zx, zy):
    result = matrices.identity()
    result.data[0][1] = xy
    result.data[0][2] = xz
    result.data[1][0] = yx
    result.data[1][2] = yz
    result.data[2][0] = zx
    result.data[2][1] = zy
    return result

def view_transform(frm, to, up):     # 'from' is a keyword in Python...
    forward = (to - frm).normalize()
    left = forward.cross(up.normalize())
    true_up = left.cross(forward)

    orientation = matrices.matrix()
    orientation.data[0] = [    left.x,     left.y,     left.z, 0]
    orientation.data[1] = [ true_up.x,  true_up.y,  true_up.z, 0]
    orientation.data[2] = [-forward.x, -forward.y, -forward.z, 0]
    orientation.data[3] = [         0,          0,          0, 1]

    return orientation * translation(-frm.x, -frm.y, -frm.z)

class TransformationsTestCase(unittest.TestCase):
    def test_multiplying_by_a_translation_matrix(self):
        transform = translation(5, -3, 2)
        p = tuples.point(-3, 4, 5)

        self.assertEqual(transform * p, tuples.point(2, 1, 7))

    def test_multiplying_by_inverse_of_a_translation_matrix(self):
        transform = translation(5, -3, 2)
        inv = transform.inverse()
        p = tuples.point(-3, 4, 5)

        self.assertEqual(inv * p, tuples.point(-8, 7, 3))

    def test_translation_does_not_affect_vectors(self):
        transform = translation(5, -3, 2)
        v = tuples.vector(-3, 4, 5)

        self.assertEqual(transform * v, v)

    def test_a_scaling_matrix_applied_to_a_point(self):
        transform = scaling(2, 3, 4)
        p = tuples.point(-4, 6, 8)

        self.assertEqual(transform * p, tuples.point(-8, 18, 32))

    def test_a_scaling_matrix_applied_to_a_vector(self):
        transform = scaling(2, 3, 4)
        v = tuples.vector(-4, 6, 8)

        self.assertEqual(transform * v, tuples.vector(-8, 18, 32))

    def test_multiplying_by_inverse_of_scaling_matrix(self):
        transform = scaling(2, 3, 4)
        inv = transform.inverse()
        v = tuples.vector(-4, 6, 8)

        self.assertEqual(inv * v, tuples.vector(-2, 2, 2))

    def test_reflection_is_negative_scaling(self):
        transform = scaling(-1, 1, 1)
        v = tuples.vector(2, 3, 4)

        self.assertEqual(transform * v, tuples.vector(-2, 3, 4))

    def test_rotating_a_point_around_x_axis(self):
        p = tuples.point(0, 1, 0)

        half_quarter = rotation_x(math.pi / 4)
        full_quarter = rotation_x(math.pi / 2)

        self.assertEqual(half_quarter * p, tuples.point(0, math.sqrt(2)/2, math.sqrt(2)/2))
        self.assertEqual(full_quarter * p, tuples.point(0, 0, 1))

    def test_inverse_of_x_rotation_rotates_in_opposite_direction(self):
        p = tuples.point(0, 1, 0)

        half_quarter = rotation_x(math.pi / 4)
        inver = half_quarter.inverse()

        self.assertEqual(inver * p, tuples.point(0, math.sqrt(2)/2, -math.sqrt(2)/2))

    def test_rotating_a_point_around_y_axis(self):
        p = tuples.point(0, 0, 1)

        half_quarter = rotation_y(math.pi / 4)
        full_quarter = rotation_y(math.pi / 2)

        self.assertEqual(half_quarter * p, tuples.point(math.sqrt(2)/2, 0, math.sqrt(2)/2))
        self.assertEqual(full_quarter * p, tuples.point(1, 0, 0))

    def test_rotating_a_point_around_z_axis(self):
        p = tuples.point(0, 1, 0)

        half_quarter = rotation_z(math.pi / 4)
        full_quarter = rotation_z(math.pi / 2)

        self.assertEqual(half_quarter * p, tuples.point(-math.sqrt(2)/2, math.sqrt(2)/2, 0))
        self.assertEqual(full_quarter * p, tuples.point(-1, 0, 0))

    def test_a_shearing_transformation_moves_x_in_proportion_to_y(self):
        transform = shearing(1, 0, 0, 0, 0, 0)
        p = tuples.point(2, 3, 4)

        self.assertEqual(transform * p, tuples.point(5, 3, 4))

    def test_a_shearing_transformation_moves_x_in_proportion_to_z(self):
        transform = shearing(0, 1, 0, 0, 0, 0)
        p = tuples.point(2, 3, 4)

        self.assertEqual(transform * p, tuples.point(6, 3, 4))

    def test_a_shearing_transformation_moves_y_in_proportion_to_x(self):
        transform = shearing(0, 0, 1, 0, 0, 0)
        p = tuples.point(2, 3, 4)

        self.assertEqual(transform * p, tuples.point(2, 5, 4))

    def test_a_shearing_transformation_moves_y_in_proportion_to_z(self):
        transform = shearing(0, 0, 0, 1, 0, 0)
        p = tuples.point(2, 3, 4)

        self.assertEqual(transform * p, tuples.point(2, 7, 4))

    def test_a_shearing_transformation_moves_z_in_proportion_to_x(self):
        transform = shearing(0, 0, 0, 0, 1, 0)
        p = tuples.point(2, 3, 4)

        self.assertEqual(transform * p, tuples.point(2, 3, 6))

    def test_a_shearing_transformation_moves_z_in_proportion_to_y(self):
        transform = shearing(0, 0, 0, 0, 0, 1)
        p = tuples.point(2, 3, 4)

        self.assertEqual(transform * p, tuples.point(2, 3, 7))

    def test_individual_transformations_are_applied_in_sequence(self):
        p = tuples.point(1, 0, 1)
        a = rotation_x(math.pi / 2)
        b = scaling(5, 5, 5)
        c = translation(10, 5, 7)

        p2 = a * p
        self.assertEqual(p2, tuples.point(1, -1, 0))

        p3 = b * p2
        self.assertEqual(p3, tuples.point(5, -5, 0))

        p4 = c * p3
        self.assertEqual(p4, tuples.point(15, 0, 7))

    def test_chained_transformations_applied_in_reverse_order(self):
        p = tuples.point(1, 0, 1)
        a = rotation_x(math.pi / 2)
        b = scaling(5, 5, 5)
        c = translation(10, 5, 7)

        t = c * b * a

        self.assertEqual(t * p, tuples.point(15, 0, 7))

    def test_transformation_matrix_for_default_view(self):
        frm = tuples.point(0, 0, 0)
        to = tuples.point(0, 0, -1)
        up = tuples.vector(0, 1, 0)

        t = view_transform(frm, to, up)

        self.assertEqual(t, matrices.identity())

    def test_transformation_matrix_looking_positive_z(self):
        frm = tuples.point(0, 0, 0)
        to = tuples.point(0, 0, 1)
        up = tuples.vector(0, 1, 0)

        t = view_transform(frm, to, up)

        self.assertEqual(t, scaling(-1, 1, -1))

    def test_view_transformation_moves_the_world(self):
        frm = tuples.point(0, 0, 8)
        to = tuples.point(0, 0, 0)
        up = tuples.vector(0, 1, 0)

        t = view_transform(frm, to, up)

        self.assertEqual(t, translation(0, 0, -8))

    def test_arbitrary_view_transformation(self):
        frm = tuples.point(1, 3, 2)
        to = tuples.point(4, -2, 8)
        up = tuples.vector(1, 1, 0)

        t = view_transform(frm, to, up)

        result = matrices.matrix()
        result.data[0] = [-0.50709, 0.50709,  0.67612, -2.36643]
        result.data[1] = [ 0.76772, 0.60609,  0.12122, -2.82843]
        result.data[2] = [-0.35857, 0.59761, -0.71714,  0.00000]
        result.data[3] = [ 0.00000, 0.00000,  0.00000,  1.00000]

        self.assertEqual(t, result)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
