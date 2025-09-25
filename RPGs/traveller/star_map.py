import unittest
from star_system import StarSystem

# in the three-axis system:
#  * the three coordinates sum to zero
#  * the distance from origin is max(|x|, |y|, |z|)

# the origin is of course (0,0,0)
# the six surrounding coordinates are:
# (0, 1, -1), (0, -1, 1)
# (1, 0, -1), (-1, 0, 1)
# (1, -1, 0), (-1, 1, 0)

# the axial rows are straightforward. one
# coordinate is zero, and the other two are
# +x/-x. So:
# (0,x,-x) & (0,-x,x)
# (x,0,-x) & (-x,0,x)
# (x,-x,0) & (-x,x,0)

# A ring of hexes at a given distance from a
# central origin hex contains six axial hexes
# and a variable number of edge hexes. There 
# are (range-1)*6 such hexes, so 0 at range 1,
# 6 at range 2, 12 at range 3, etc. So the total
# number of hexes in a ring are equal to: 
#   6 + (range-1)*6.

# As noted above, axial hexes are trivial to
# figure out. Just all the valid variations of
# +range, -range, and zero (one of each per coord).

# Edge hexes are trickier. They are grouped into
# six 'pie slices,' each bounded by two different
# axes. If we call the axes red, blue, green, then
# the slices are:
#   +blue, +red     (-green)
#   -red, -green    (+blue)
#   +blue, +green   (-red)
#   -blue, -red     (+green)
#   +red, +green    (-blue)
#   -blue, -green   (+red)
#
# (Each slice also sits entirely to one side of the
#  third 'non-bounding' axis, as noted in parens above.)
#
# The edge coordinates at a given range are the sum of
# the corresponding axial hexes along that span, just
# like with Cartesian coordinates. It's the same sort
# of transform - go over 3 on the x-axis, and up 2 on
# the y-axis, and arrive at (3,2). Instead we would
# go over 3 on the blue-axis, and up 2 on the red-axis,
# and arrive at (3,2,-5). The third coordinate is 
# really just a checksum and can be calculated given
# the other two, since sum(a,b,c) = 0. Tricky bit is this
# hex is _five_ away from the origin, so arriving at it
# from just the range value is tricky.

# An alternate strategy:
# * the complete set of coordinates at a given range x
#   (including invalid coordinates) is given by:
#   [(a,b,c) for a in range(-x,x+1) 
#            for b in range(-x,x+1)
#            for c in range(-x,x+1)]
#  
# * the length of this list is (2x+1)^3, so
#   27 (3 cubed) at range 1, 125 (5 cubed) at range 2, etc.
#
# * we can then filter out the invalid members with a 
#   simple test, and voila! There's the list at range x.
#
#   [a for a in full_list if sum(a)==0]
#
# Then, if we want to find hexes around some arbitrary
# point, we just translate everything to that new origin
# (by adding the new origin to every coordinate of course).

class StarMap:
    def __init__(self, systems):
        # TO_DO: consider validating coordinates before adding...
        self.systems = systems
        for key in self.systems.keys():
            if not StarMap.valid_coordinate(key):
                raise ValueError(f"Invalid three-axis coordinate: {key}")

    # halfway step - final JIT approach should be:
    # * get all coordinates up to range surrounding origin
    # * three possibilities:
    #   1) in dictionary, and StarSystem - add to result
    #   2) in dictionary, and None - leave out of result
    #   3) not in dictionary - generate, handle as 1 & 2
    def get_systems_within_range(self, origin, distance):
        result = []
        for coord in self.systems:
            system = self.systems[coord]
            if (StarMap.distance_between(origin, coord) <= distance and
                coord != origin and
                system is not None):
                result.append(system)
        return result

    def get_system_at_coordinate(self, coordinate):
        return self.systems[coordinate]

    @classmethod
    def distance_between(cls, first, second):
        transformed = (second[0]-first[0],
                       second[1]-first[1],
                       second[2]-first[2])
        return max(abs(transformed[0]),
                   abs(transformed[1]),
                   abs(transformed[2]))

    @classmethod
    def valid_coordinate(cls, coord):
        return sum(coord) == 0

    @classmethod
    def get_coordinates_within_range(cls, origin, range_):
        result = []
        for i in range(range_):
            result += StarMap.get_coordinates_at_range(origin, i+1)
        return result

    @classmethod
    def get_coordinates_at_range(cls, origin, range_):
        result = StarMap.axis_hexes(range_) + StarMap.edge_hexes(range_)
        return result

    @classmethod
    def axis_hexes(cls, range_):
        return [(0,range_,-range_),
                (0,-range_,range_),
                (range_,0,-range_),
                (-range_,0,range_),
                (range_,-range_,0),
                (-range_,range_,0)]

    @classmethod
    def edge_hexes(cls, range_):
        result = []
        for i in range(range_-1):
            for _ in range(6):
                result.append((0,0,0))    # <== PLACEHOLDER
        return result

    @classmethod
    def get_all_coords(cls, radius):
        return [(a,b,c) for a in range(-radius,radius+1) 
                        for b in range(-radius,radius+1)
                        for c in range(-radius,radius+1)]

class StarMapTestCase(unittest.TestCase):
    def setUp(self):
        StarMapTestCase.star_map1 = StarMap({
            (0,0,0)  : StarSystem("Yorbund", (0,0,0), "A", 5, 5, 5, 5),
            (0,1,-1) : None,
            (0,-1,1) : StarSystem("Mithril", (0,-1,1), "A", 5, 5, 5, 5),
            (1,0,-1) : StarSystem("Kinorb", (1,0,-1), "A", 5, 5, 5, 5),
            (-1,0,1) : None,
            (1,-1,0) : None,
            (-1,1,0) : StarSystem("Aramis", (-1,1,0), "A", 5, 5, 5, 5)
            })

        StarMapTestCase.star_map2 = StarMap({
            (0,0,0)  : StarSystem("Yorbund", (0,0,0), "A", 5, 5, 5, 5),
            (0,1,-1) : None,
            (0,-1,1) : None,
            (1,0,-1) : None,
            (-1,0,1) : None,
            (1,-1,0) : None,
            (-1,1,0) : None,
            })

    def test_constructor(self):
        star_map1 = StarMapTestCase.star_map1
        self.assertTrue(isinstance(star_map1, StarMap))

    def test_get_systems_within_range(self):
        star_map1 = StarMapTestCase.star_map1

        systems = star_map1.get_systems_within_range((0,0,0), 1)
        self.assertEqual(len(systems), 3)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(isinstance(systems[1], StarSystem))
        self.assertTrue(isinstance(systems[2], StarSystem))
        self.assertTrue(systems[0].name in ("Kinorb", "Aramis", "Mithril"))
        self.assertTrue(systems[1].name in ("Kinorb", "Aramis", "Mithril"))
        self.assertTrue(systems[2].name in ("Kinorb", "Aramis", "Mithril"))

        systems = star_map1.get_systems_within_range((1,0,-1), 1)
        self.assertEqual(len(systems), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertEqual(systems[0].name, "Yorbund")

        systems = star_map1.get_systems_within_range((-1,1,0), 1)
        self.assertEqual(len(systems), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertEqual(systems[0].name, "Yorbund")

        systems = star_map1.get_systems_within_range((0,-1,1), 1)
        self.assertEqual(len(systems), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertEqual(systems[0].name, "Yorbund")

        systems = star_map1.get_systems_within_range((0,-1,1), 2)
        self.assertEqual(len(systems), 3)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(isinstance(systems[1], StarSystem))
        self.assertTrue(isinstance(systems[2], StarSystem))
        self.assertTrue(systems[0].name in ("Kinorb", "Aramis", "Yorbund"))
        self.assertTrue(systems[1].name in ("Kinorb", "Aramis", "Yorbund"))
        self.assertTrue(systems[2].name in ("Kinorb", "Aramis", "Yorbund"))

    def test_get_systems_within_range_with_None(self):
        star_map2 = StarMapTestCase.star_map2

        systems = star_map2.get_systems_within_range((0,0,0), 1)
        self.assertEqual(len(systems), 0)

    def test_get_system_at_coordinate(self):
        star_map1 = StarMapTestCase.star_map1

        world = star_map1.get_system_at_coordinate((0,0,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")

        world = star_map1.get_system_at_coordinate((1,0,-1))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Kinorb")

        world = star_map1.get_system_at_coordinate((-1,1,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Aramis")

        world = star_map1.get_system_at_coordinate((0,-1,1))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Mithril")

    def test_get_systems_with_None(self):
        star_map2 = StarMapTestCase.star_map2

        world = star_map2.get_system_at_coordinate((0,0,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")

        world = star_map2.get_system_at_coordinate((0,1,-1))
        self.assertTrue(world is None)

        world = star_map2.get_system_at_coordinate((0,-1,1))
        self.assertTrue(world is None)

        world = star_map2.get_system_at_coordinate((1,0,-1))
        self.assertTrue(world is None)

        world = star_map2.get_system_at_coordinate((-1,0,1))
        self.assertTrue(world is None)

        world = star_map2.get_system_at_coordinate((1,-1,0))
        self.assertTrue(world is None)

        world = star_map2.get_system_at_coordinate((-1,1,0))
        self.assertTrue(world is None)

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

        dist = StarMap.distance_between((1,0,-1), (2,0,-2))
        self.assertEqual(dist,1)

    def test_valid_coordinate(self):
        self.assertTrue(StarMap.valid_coordinate((0,0,0)))
        self.assertFalse(StarMap.valid_coordinate((1,0,0)))

    def test_invalid_ctor_call(self):
        self.assertRaises(ValueError, StarMap, {(1,0,0):None})

    def test_get_coordinates_within_range(self):
        coords = StarMap.get_coordinates_within_range((0,0,0), 1)
        self.assertEqual(len(coords), 6)
        self.assertTrue((0,1,-1) in coords)
        self.assertTrue((0,-1,1) in coords)
        self.assertTrue((1,0,-1) in coords)
        self.assertTrue((-1,0,1) in coords)
        self.assertTrue((1,-1,0) in coords)
        self.assertTrue((-1,1,0) in coords)

        coords = StarMap.get_coordinates_within_range((0,0,0), 2)
        self.assertEqual(len(coords), 18)
        self.assertTrue((0,2,-2) in coords)
        self.assertTrue((0,-2,2) in coords)
        self.assertTrue((2,0,-2) in coords)
        self.assertTrue((-2,0,2) in coords)
        self.assertTrue((2,-2,0) in coords)
        self.assertTrue((-2,2,0) in coords)

        coords = StarMap.get_coordinates_within_range((0,0,0), 3)
        self.assertEqual(len(coords), 36)
        self.assertTrue((0,3,-3) in coords)
        self.assertTrue((0,-3,3) in coords)
        self.assertTrue((3,0,-3) in coords)
        self.assertTrue((-3,0,3) in coords)
        self.assertTrue((3,-3,0) in coords)
        self.assertTrue((-3,3,0) in coords)

    def test_get_all_coords(self):
        coords = StarMap.get_all_coords(1)
        self.assertEqual(len(coords), 27)   # 3 cubed

        coords = StarMap.get_all_coords(2)
        self.assertEqual(len(coords), 125)  # 5 cubed

        coords = StarMap.get_all_coords(3)
        self.assertEqual(len(coords), 343)  # 7 cubed

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
