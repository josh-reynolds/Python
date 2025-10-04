"""Contains tests for the star_map module."""
import unittest
from star_map import StarMap, StarSystemFactory
from star_system import StarSystem, DeepSpace

class StarMapTestCase(unittest.TestCase):
    """Tests StarMap class."""
    def setUp(self):
        StarMapTestCase.star_map1 = StarMap({
            (0,0,0)  : StarSystemFactory.create("Yorbund", (0,0,0), "A", 5, 5, 5, 5, 5, 5, 5),
            (0,1,-1) : DeepSpace((0,1,-1)),
            (0,-1,1) : StarSystemFactory.create("Mithril", (0,-1,1), "A", 5, 5, 5, 5, 5, 5, 5),
            (1,0,-1) : StarSystemFactory.create("Kinorb", (1,0,-1), "A", 5, 5, 5, 5, 5, 5, 5),
            (-1,0,1) : DeepSpace((-1,0,1)),
            (1,-1,0) : DeepSpace((1,-1,0)),
            (-1,1,0) : StarSystemFactory.create("Aramis", (-1,1,0), "A", 5, 5, 5, 5, 5, 5, 5)
            })

        StarMapTestCase.star_map2 = StarMap({
            (0,0,0)  : StarSystemFactory.create("Yorbund", (0,0,0), "A", 5, 5, 5, 5, 5, 5, 5),
            (0,1,-1) : DeepSpace((0,1,-1)),
            (0,-1,1) : DeepSpace((0,-1,1)),
            (1,0,-1) : DeepSpace((1,0,-1)),
            (-1,0,1) : DeepSpace((-1,0,1)),
            (1,-1,0) : DeepSpace((1,-1,0)),
            (-1,1,0) : DeepSpace((-1,1,0)),
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

        systems = star_map1.get_systems_within_range((-1,1,0), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))

        systems = star_map1.get_systems_within_range((0,-1,1), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))

        systems = star_map1.get_systems_within_range((0,-1,1), 2)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(isinstance(systems[1], StarSystem))
        self.assertTrue(isinstance(systems[2], StarSystem))

    def test_get_systems_within_range_with_deepspace(self):
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

    def test_get_systems_with_deepspace(self):
        star_map2 = StarMapTestCase.star_map2

        world = star_map2.get_system_at_coordinate((0,0,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")

        world = star_map2.get_system_at_coordinate((0,1,-1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate((0,-1,1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate((1,0,-1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate((-1,0,1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate((1,-1,0))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate((-1,1,0))
        self.assertTrue(isinstance(world, DeepSpace))

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
        self.assertEqual(len(worlds), 100)

        systems = [s for s in worlds if isinstance(s, StarSystem)]
        self.assertTrue(len(systems) < 75)
        self.assertTrue(len(systems) > 25)

        for item in worlds:
            self.assertTrue(type(item) in [DeepSpace, StarSystem])

    def test_get_all_systems(self):
        star_map1 = StarMapTestCase.star_map1
        systems = star_map1.get_all_systems()
        self.assertEqual(len(systems), 4)
        self.assertEqual(systems[0], StarSystemFactory.create("Aramis",
                                                              (-1,1,0),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))
        self.assertEqual(systems[1], StarSystemFactory.create("Mithril",
                                                              (0,-1,1),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))
        self.assertEqual(systems[2], StarSystemFactory.create("Yorbund",
                                                              (0,0,0),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))
        self.assertEqual(systems[3], StarSystemFactory.create("Kinorb",
                                                              (1,0,-1),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))

class StarSystemFactoryTestCase(unittest.TestCase):
    """Tests StarSystemFactory class."""

    def test_generate(self):
        system = StarSystemFactory.generate((0,0,0))
        self.assertEqual(system.coordinate, (0,0,0))

        self.assertTrue(system.starport in ('A', 'B', 'C', 'D', 'E', 'X'))

        self.assertGreaterEqual(system.size, 0)
        self.assertLessEqual(system.size,10)

        self.assertGreaterEqual(system.atmosphere, 0)
        self.assertLessEqual(system.atmosphere, 12)

        self.assertGreaterEqual(system.hydrographics, 0)
        self.assertLessEqual(system.hydrographics, 10)

        self.assertGreaterEqual(system.population, 0)
        self.assertLessEqual(system.population, 10)

        self.assertGreaterEqual(system.government, 0)
        self.assertLessEqual(system.government, 13)

        self.assertGreaterEqual(system.law, 0)
        self.assertLessEqual(system.law, 9)

        self.assertGreaterEqual(system.tech, 0)
        self.assertLessEqual(system.tech, 18)

    def test_create(self):
        world = StarSystemFactory.create("Yorbund", (0,0,0), "A", 8, 7, 5, 9, 5, 5, 10)

        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")
        self.assertEqual(world.coordinate, (0,0,0))
        self.assertEqual(world.starport, "A")
        self.assertEqual(world.size, 8)
        self.assertEqual(world.atmosphere, 7)
        self.assertEqual(world.hydrographics, 5)
        self.assertEqual(world.population, 9)
        self.assertEqual(world.government, 5)
        self.assertEqual(world.law, 5)
        self.assertEqual(world.tech, 10)
        self.assertEqual(world.gas_giant, True)
        self.assertEqual(world.agricultural, False)
        self.assertEqual(world.nonagricultural, False)
        self.assertEqual(world.industrial, True)
        self.assertEqual(world.nonindustrial, False)
        self.assertEqual(world.rich, False)
        self.assertEqual(world.poor, False)

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

