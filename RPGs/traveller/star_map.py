import unittest

class StarMap:
    pass

class StarMapTestCase(unittest.TestCase):
    def test_constructor(self):
        star_map = StarMap()
        self.assertTrue(isinstance(star_map, StarMap))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
