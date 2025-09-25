import unittest
from random import randint
from star_system import StarSystem
from utilities import die_roll

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
#   a.remove((0,0,0))                   # probably also want
#                                       # to drop the origin...
#
# Then, if we want to find hexes around some arbitrary
# point, we just translate everything to that new origin
# (by adding the new origin to every coordinate of course).

class StarSystemFactory:
    @classmethod
    def generate(cls, coordinate):
        name = "Test"

        roll = die_roll() + die_roll()
        if roll <= 4:
            starport = "A"
        elif roll <= 6:
            starport = "B"
        elif roll <= 8:
            starport = "C"
        elif roll <= 9:
            starport = "D"
        elif roll <= 11:
            starport = "E"
        else:
            starport = "X"

        atmosphere = 5
        hydrographics = 5
        population = 5
        government = 5
        gas_giant = True
        return StarSystem(name, coordinate, starport, atmosphere,
                          hydrographics, population, government, gas_giant)

class StarMap:
    def __init__(self, systems):
        self.systems = systems
        for key in self.systems.keys():
            if not StarMap.valid_coordinate(key):
                raise ValueError(f"Invalid three-axis coordinate: {key}")

    def get_systems_within_range(self, origin, distance):
        result = []
        for coord in StarMap.get_coordinates_within_range(origin, distance):
            if coord in self.systems:
                if self.systems[coord] is not None:
                    result.append(self.systems[coord])
            else:
                system = StarMap.generate_new_system(coord)
                self.systems[coord] = system
                if system is not None:
                    result.append(system)
        return result

    def get_system_at_coordinate(self, coordinate):
        return self.systems[coordinate]

    def get_all_systems(self):
        systems = [s for i,(k,s) in enumerate(self.systems.items()) if s is not None]
        systems = sorted(systems, key=lambda system: system.coordinate)
        return systems

    @classmethod
    def generate_new_system(cls, coordinate):
        if randint(1,6) >= 4:
            return StarSystemFactory.generate(coordinate)
        return None

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

    # TO_DO: should we default origin param to (0,0,0)?
    @classmethod
    def get_coordinates_within_range(cls, origin, radius):
        full_list = StarMap.get_all_coords(radius)

        filtered = [a for a in full_list if sum(a)==0]
        filtered.remove((0,0,0))

        translated = [(f[0] + origin[0],
                       f[1] + origin[1],
                       f[2] + origin[2]) for f in filtered]

        return translated

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
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(systems[0].name in ("Yorbund", "Test"))

        systems = star_map1.get_systems_within_range((-1,1,0), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(systems[0].name in ("Yorbund", "Test"))

        systems = star_map1.get_systems_within_range((0,-1,1), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(systems[0].name in ("Yorbund", "Test"))

        systems = star_map1.get_systems_within_range((0,-1,1), 2)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(isinstance(systems[1], StarSystem))
        self.assertTrue(isinstance(systems[2], StarSystem))
        self.assertTrue(systems[0].name in ("Kinorb", "Aramis", "Yorbund", "Test"))
        self.assertTrue(systems[1].name in ("Kinorb", "Aramis", "Yorbund", "Test"))
        self.assertTrue(systems[2].name in ("Kinorb", "Aramis", "Yorbund", "Test"))

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
        self.assertTrue((0,1,-1) in coords) # axial hexes
        self.assertTrue((0,-1,1) in coords)
        self.assertTrue((1,0,-1) in coords)
        self.assertTrue((-1,0,1) in coords)
        self.assertTrue((1,-1,0) in coords)
        self.assertTrue((-1,1,0) in coords) # no edge hexes

        coords = StarMap.get_coordinates_within_range((0,0,0), 2)
        self.assertEqual(len(coords), 18)
        self.assertTrue((0,2,-2) in coords) # axial hexes
        self.assertTrue((0,-2,2) in coords)
        self.assertTrue((2,0,-2) in coords)
        self.assertTrue((-2,0,2) in coords)
        self.assertTrue((2,-2,0) in coords)
        self.assertTrue((-2,2,0) in coords)
        self.assertTrue((1,1,-2) in coords) # select edge hexes
        self.assertTrue((-1,-1,2) in coords)
        self.assertTrue((2,-1,-1) in coords)

        coords = StarMap.get_coordinates_within_range((0,0,0), 3)
        self.assertEqual(len(coords), 36)
        self.assertTrue((0,3,-3) in coords) # axial hexes
        self.assertTrue((0,-3,3) in coords)
        self.assertTrue((3,0,-3) in coords)
        self.assertTrue((-3,0,3) in coords)
        self.assertTrue((3,-3,0) in coords)
        self.assertTrue((-3,3,0) in coords)
        self.assertTrue((2,1,-3) in coords) # select edge hexes
        self.assertTrue((2,-3,1) in coords)
        self.assertTrue((-3,2,1) in coords)

    def test_get_all_coords(self):
        coords = StarMap.get_all_coords(1)
        self.assertEqual(len(coords), 27)   # 3 cubed

        coords = StarMap.get_all_coords(2)
        self.assertEqual(len(coords), 125)  # 5 cubed

        coords = StarMap.get_all_coords(3)
        self.assertEqual(len(coords), 343)  # 7 cubed

    def test_translated_coords(self):
        coords = StarMap.get_coordinates_within_range((-1,-1,2), 1)
        self.assertEqual(len(coords), 6)
        self.assertTrue((0,-1,1) in coords) # axial hexes
        self.assertTrue((-1,0,1) in coords)
        self.assertTrue((-2,0,2) in coords)
        self.assertTrue((-2,-1,3) in coords)
        self.assertTrue((-1,-2,3) in coords)
        self.assertTrue((0,-2,2) in coords) # no edge hexes

    def test_generate_new_system(self):
        # function output is random, so we can only test
        # sample sizes - guessing at a reasonable bound,
        # but this could occasionally fail nontheless
        worlds = []
        for _ in range(100):
            world = StarMap.generate_new_system((0,0,0))
            if world is not None:
                worlds.append(world)
        self.assertTrue(len(worlds) < 75)
        self.assertTrue(len(worlds) > 25)

        for item in worlds:
            self.assertTrue(isinstance(item, StarSystem))

    def test_get_all_systems(self):
        star_map1 = StarMapTestCase.star_map1
        systems = star_map1.get_all_systems()
        self.assertEqual(len(systems), 4)
        self.assertEqual(systems[0], StarSystem("Aramis", (-1,1,0), "A", 5, 5, 5, 5))
        self.assertEqual(systems[1], StarSystem("Mithril", (0,-1,1), "A", 5, 5, 5, 5))
        self.assertEqual(systems[2], StarSystem("Yorbund", (0,0,0), "A", 5, 5, 5, 5))
        self.assertEqual(systems[3], StarSystem("Kinorb", (1,0,-1), "A", 5, 5, 5, 5))

class StarSystemFactoryTestCase(unittest.TestCase):
    def test_generate(self):
        system = StarSystemFactory.generate((0,0,0))
        self.assertEqual(system.name, "Test")
        self.assertEqual(system.coordinate, (0,0,0))
        self.assertTrue(system.starport in ('A', 'B', 'C', 'D', 'E', 'X'))
        self.assertEqual(system.atmosphere, 5)
        self.assertEqual(system.hydrographics, 5)
        self.assertEqual(system.population, 5)
        self.assertEqual(system.government, 5)
        self.assertTrue(system.gas_giant)

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
