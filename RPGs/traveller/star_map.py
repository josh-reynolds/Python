import unittest
from star_system import StarSystem

class StarMap:
    def get_systems_within_range(self, origin, distance):
        return [StarSystem("Kinorb", "A", 5, 5, 5, 5)]

class StarMapTestCase(unittest.TestCase):
    def setUp(self):
        StarMapTestCase.star_map = StarMap()

    def test_constructor(self):
        star_map = StarMapTestCase.star_map
        self.assertTrue(isinstance(star_map, StarMap))

    def test_get_systems_within_range(self):
        star_map = StarMapTestCase.star_map
        systems = star_map.get_systems_within_range((0,0,0), 1)
        self.assertEqual(len(systems), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
