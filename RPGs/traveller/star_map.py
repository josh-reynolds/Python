import unittest
from star_system import StarSystem

class StarMap:
    def get_systems_within_range(self, origin, distance):
        return [StarSystem("Kinorb", "A", 5, 5, 5, 5)]

    def get_system_at_coordinate(self, coordinate):
        if coordinate == (0,0,0):
            return StarSystem("Yorbund", "A", 5, 5, 5, 5)
        return StarSystem("Kinorb", "A", 5, 5, 5, 5)


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
        self.assertEqual(systems[0].name, "Kinorb")

    def test_get_system_at_coordinate(self):
        star_map = StarMapTestCase.star_map

        world = star_map.get_system_at_coordinate((0,0,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")

        world = star_map.get_system_at_coordinate((1,0,-1))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Kinorb")

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
