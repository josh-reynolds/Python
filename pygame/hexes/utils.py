import unittest

EPSILON = 0.00001

def flequal(a, b):
    if abs(a - b) < EPSILON:
        return True
    return False

def image_to_file(image, filename):
    f = open(filename, "w")
    lines = image.to_ppm()
    for line in lines:
        f.write(line + "\n")
    f.close()

class UtilsTestCase(unittest.TestCase):
    def test_almost_equal_floats_return_true(self):
        a = 0.12345
        b = 0.12346

        self.assertTrue(flequal(a, b))

    def test_unequal_floats_return_false(self):
        a = 0.1234
        b = 0.1235

        self.assertFalse(flequal(a, b))

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
