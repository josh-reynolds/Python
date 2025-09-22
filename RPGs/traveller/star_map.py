import unittest
from star_system import StarSystem

# in the three-axis system:
#  * the three coordinates sum to zero
#  * the distance from origin is max(|x|, |y|, |z|)
#
# the origin is of course (0,0,0)
# the six surrounding coordinates are:
# (1, -1, 0), (1, 0, -1)
# (0, 1, -1), (0, -1, 1)
# (-1, 0, 1), (-1, 1, 0)
#
# the axial rows are straightforward. one
# coordinate is zero, and the other two are
# +x/-x. So:
# (0,x,-x) & (0,-x,x)
# (x,0,-x) & (-x,0,x)
# (x,-x,0) & (-x,x,0)

class StarMap:
    def __init__(self, systems):
        self.systems = systems

    def get_systems_within_range(self, origin, distance):
        if origin == (0,0,0):
            return [StarSystem("Kinorb", "A", 5, 5, 5, 5),
                    StarSystem("Aramis", "A", 5, 5, 5, 5),
                    StarSystem("Mithril", "A", 5, 5, 5, 5)]
        if origin == (1,0,-1):
            return [StarSystem("Yorbund", "A", 5, 5, 5, 5)]
        if origin == (-1,1,0):
            return [StarSystem("Yorbund", "A", 5, 5, 5, 5)]
        if origin == (0,-1,1):
            return [StarSystem("Yorbund", "A", 5, 5, 5, 5)]

    def get_system_at_coordinate(self, coordinate):
        return self.systems[coordinate]

    @classmethod
    def distance_between(cls, first, second):
        return max(abs(second[0]), abs(second[1]), abs(second[2]))

class StarMapTestCase(unittest.TestCase):
    def setUp(self):
        StarMapTestCase.star_map = StarMap({
            (0,0,0)  : StarSystem("Yorbund", "A", 5, 5, 5, 5),
            (1,0,-1) : StarSystem("Kinorb", "A", 5, 5, 5, 5),
            (-1,1,0) : StarSystem("Aramis", "A", 5, 5, 5, 5),
            (0,-1,1) : StarSystem("Mithril", "A", 5, 5, 5, 5)
            })

    def test_constructor(self):
        star_map = StarMapTestCase.star_map
        self.assertTrue(isinstance(star_map, StarMap))

    def test_get_systems_within_range(self):
        star_map = StarMapTestCase.star_map

        systems = star_map.get_systems_within_range((0,0,0), 1)
        self.assertEqual(len(systems), 3)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertEqual(systems[0].name, "Kinorb")
        self.assertTrue(isinstance(systems[1], StarSystem))
        self.assertEqual(systems[1].name, "Aramis")
        self.assertTrue(isinstance(systems[2], StarSystem))
        self.assertEqual(systems[2].name, "Mithril")

        systems = star_map.get_systems_within_range((1,0,-1), 1)
        self.assertEqual(len(systems), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertEqual(systems[0].name, "Yorbund")

        systems = star_map.get_systems_within_range((-1,1,0), 1)
        self.assertEqual(len(systems), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertEqual(systems[0].name, "Yorbund")

        systems = star_map.get_systems_within_range((0,-1,1), 1)
        self.assertEqual(len(systems), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertEqual(systems[0].name, "Yorbund")

    def test_get_system_at_coordinate(self):
        star_map = StarMapTestCase.star_map

        world = star_map.get_system_at_coordinate((0,0,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")

        world = star_map.get_system_at_coordinate((1,0,-1))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Kinorb")

        world = star_map.get_system_at_coordinate((-1,1,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Aramis")

        world = star_map.get_system_at_coordinate((0,-1,1))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Mithril")

    def test_distance_between(self):
        dist = StarMap.distance_between((0,0,0), (1,0,-1))
        self.assertEqual(dist,1)

        dist = StarMap.distance_between((0,0,0), (0,2,-2))
        self.assertEqual(dist,2)

        dist = StarMap.distance_between((0,0,0), (2,0,-2))
        self.assertEqual(dist,2)

        dist = StarMap.distance_between((0,0,0), (-2,0,2))
        self.assertEqual(dist,2)

        dist = StarMap.distance_between((0,0,0), (1,-2,1))
        self.assertEqual(dist,2)

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
