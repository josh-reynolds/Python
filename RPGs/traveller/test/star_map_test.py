"""Contains tests for the star_map module."""
import unittest
from src.coordinate import Coordinate
from src.star_map import StarMap, Subsector, subsector_from
from src.star_system import StarSystem, DeepSpace
from src.star_system_factory import StarSystemFactory

class StarMapTestCase(unittest.TestCase):
    """Tests StarMap class."""

    star_map1: StarMap
    star_map2: StarMap

    def setUp(self) -> None:
        """Create a fixture to test the StarMap class."""
        StarMapTestCase.star_map1 = StarMap({
            Coordinate(0,0,0)  : StarSystemFactory.create("Yorbund",
                                                          Coordinate(0,0,0),
                                                          "A", 5, 5, 5, 5, 5, 5, 5),
            Coordinate(0,1,-1) : DeepSpace(Coordinate(0,1,-1)),
            Coordinate(0,-1,1) : StarSystemFactory.create("Mithril",
                                                          Coordinate(0,-1,1),
                                                          "A", 5, 5, 5, 5, 5, 5, 5),
            Coordinate(1,0,-1) : StarSystemFactory.create("Kinorb",
                                                          Coordinate(1,0,-1),
                                                          "A", 5, 5, 5, 5, 5, 5, 5),
            Coordinate(-1,0,1) : DeepSpace(Coordinate(-1,0,1)),
            Coordinate(1,-1,0) : DeepSpace(Coordinate(1,-1,0)),
            Coordinate(-1,1,0) : StarSystemFactory.create("Aramis",
                                                          Coordinate(-1,1,0),
                                                          "A", 5, 5, 5, 5, 5, 5, 5)
            })

        StarMapTestCase.star_map2 = StarMap({
            Coordinate(0,0,0)  : StarSystemFactory.create("Yorbund",
                                                          Coordinate(0,0,0),
                                                          "A", 5, 5, 5, 5, 5, 5, 5),
            Coordinate(0,1,-1) : DeepSpace(Coordinate(0,1,-1)),
            Coordinate(0,-1,1) : DeepSpace(Coordinate(0,-1,1)),
            Coordinate(1,0,-1) : DeepSpace(Coordinate(1,0,-1)),
            Coordinate(-1,0,1) : DeepSpace(Coordinate(-1,0,1)),
            Coordinate(1,-1,0) : DeepSpace(Coordinate(1,-1,0)),
            Coordinate(-1,1,0) : DeepSpace(Coordinate(-1,1,0)),
            })

    def test_constructor(self) -> None:
        """Test construction of a StarMap."""
        star_map1 = StarMapTestCase.star_map1
        self.assertTrue(isinstance(star_map1, StarMap))

    def test_get_systems_within_range(self) -> None:
        """Test retrieval of StarSystems within a specified range."""
        star_map1 = StarMapTestCase.star_map1

        systems = star_map1.get_systems_within_range(Coordinate(0,0,0), 1)
        self.assertEqual(len(systems), 3)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(isinstance(systems[1], StarSystem))
        self.assertTrue(isinstance(systems[2], StarSystem))
        self.assertTrue(systems[0].name in ("Kinorb", "Aramis", "Mithril"))
        self.assertTrue(systems[1].name in ("Kinorb", "Aramis", "Mithril"))
        self.assertTrue(systems[2].name in ("Kinorb", "Aramis", "Mithril"))

        systems = star_map1.get_systems_within_range(Coordinate(1,0,-1), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))

        systems = star_map1.get_systems_within_range(Coordinate(-1,1,0), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))

        systems = star_map1.get_systems_within_range(Coordinate(0,-1,1), 1)
        self.assertTrue(isinstance(systems[0], StarSystem))

        systems = star_map1.get_systems_within_range(Coordinate(0,-1,1), 2)
        self.assertTrue(isinstance(systems[0], StarSystem))
        self.assertTrue(isinstance(systems[1], StarSystem))
        self.assertTrue(isinstance(systems[2], StarSystem))

    def test_get_systems_within_range_with_deepspace(self) -> None:
        """Test retrieval of StarSystems within range when there are empty hexes."""
        star_map2 = StarMapTestCase.star_map2

        systems = star_map2.get_systems_within_range(Coordinate(0,0,0), 1)
        self.assertEqual(len(systems), 0)

    def test_get_system_at_coordinate(self) -> None:
        """Test retrieval of StarSystems by coordinate value."""
        star_map1 = StarMapTestCase.star_map1

        world = star_map1.get_system_at_coordinate(Coordinate(0,0,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")

        world = star_map1.get_system_at_coordinate(Coordinate(1,0,-1))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Kinorb")

        world = star_map1.get_system_at_coordinate(Coordinate(-1,1,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Aramis")

        world = star_map1.get_system_at_coordinate(Coordinate(0,-1,1))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Mithril")

    def test_get_systems_with_deepspace(self) -> None:
        """Test retrieval of StarSystems by coordinate when there are empty hexes."""
        star_map2 = StarMapTestCase.star_map2

        world = star_map2.get_system_at_coordinate(Coordinate(0,0,0))
        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")

        world = star_map2.get_system_at_coordinate(Coordinate(0,1,-1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate(Coordinate(0,-1,1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate(Coordinate(1,0,-1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate(Coordinate(-1,0,1))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate(Coordinate(1,-1,0))
        self.assertTrue(isinstance(world, DeepSpace))

        world = star_map2.get_system_at_coordinate(Coordinate(-1,1,0))
        self.assertTrue(isinstance(world, DeepSpace))

    # pylint: disable=W0212
    # W0212: Access to a protected member _distance_between of a client class
    def test_distance_between(self) -> None:
        """Test calculation of distance between two three-axis coordinates."""
        dist = StarMap._distance_between(Coordinate(0,0,0), Coordinate(1,0,-1))
        self.assertEqual(dist,1)

        dist = StarMap._distance_between(Coordinate(0,0,0), Coordinate(0,2,-2))
        self.assertEqual(dist,2)

        dist = StarMap._distance_between(Coordinate(0,0,0), Coordinate(2,0,-2))
        self.assertEqual(dist,2)

        dist = StarMap._distance_between(Coordinate(0,0,0), Coordinate(-2,0,2))
        self.assertEqual(dist,2)

        dist = StarMap._distance_between(Coordinate(0,0,0), Coordinate(1,-2,1))
        self.assertEqual(dist,2)

        dist = StarMap._distance_between(Coordinate(1,0,-1), Coordinate(2,0,-2))
        self.assertEqual(dist,1)

    def test_invalid_ctor_call(self) -> None:
        """Test exception thrown by invalid StarMap constructor call."""
        self.assertRaises(AttributeError, StarMap, {(1,0,0):None})

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_coordinates_within_range of a client class
    def test_get_coordinates_within_range(self) -> None:
        """Test retrieval of all valid three-axis coordinates within range of an origin hex."""
        coords = StarMap._get_coordinates_within_range(Coordinate(0,0,0), 1)
        self.assertEqual(len(coords), 6)
        self.assertTrue(Coordinate(0,1,-1) in coords) # axial hexes
        self.assertTrue(Coordinate(0,-1,1) in coords)
        self.assertTrue(Coordinate(1,0,-1) in coords)
        self.assertTrue(Coordinate(-1,0,1) in coords)
        self.assertTrue(Coordinate(1,-1,0) in coords)
        self.assertTrue(Coordinate(-1,1,0) in coords) # no edge hexes

        coords = StarMap._get_coordinates_within_range(Coordinate(0,0,0), 2)
        self.assertEqual(len(coords), 18)
        self.assertTrue(Coordinate(0,2,-2) in coords) # axial hexes
        self.assertTrue(Coordinate(0,-2,2) in coords)
        self.assertTrue(Coordinate(2,0,-2) in coords)
        self.assertTrue(Coordinate(-2,0,2) in coords)
        self.assertTrue(Coordinate(2,-2,0) in coords)
        self.assertTrue(Coordinate(-2,2,0) in coords)
        self.assertTrue(Coordinate(1,1,-2) in coords) # select edge hexes
        self.assertTrue(Coordinate(-1,-1,2) in coords)
        self.assertTrue(Coordinate(2,-1,-1) in coords)

        coords = StarMap._get_coordinates_within_range(Coordinate(0,0,0), 3)
        self.assertEqual(len(coords), 36)
        self.assertTrue(Coordinate(0,3,-3) in coords) # axial hexes
        self.assertTrue(Coordinate(0,-3,3) in coords)
        self.assertTrue(Coordinate(3,0,-3) in coords)
        self.assertTrue(Coordinate(-3,0,3) in coords)
        self.assertTrue(Coordinate(3,-3,0) in coords)
        self.assertTrue(Coordinate(-3,3,0) in coords)
        self.assertTrue(Coordinate(2,1,-3) in coords) # select edge hexes
        self.assertTrue(Coordinate(2,-3,1) in coords)
        self.assertTrue(Coordinate(-3,2,1) in coords)

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_all_coords of a client class
    def test_get_all_coords(self) -> None:
        """Test getting all potential coordinates at a given range from (0,0,0)."""
        coords = StarMap._get_all_coords(1)
        self.assertEqual(len(coords), 27)   # 3 cubed

        coords = StarMap._get_all_coords(2)
        self.assertEqual(len(coords), 125)  # 5 cubed

        coords = StarMap._get_all_coords(3)
        self.assertEqual(len(coords), 343)  # 7 cubed

    # pylint: disable=W0212
    # W0212: Access to a protected member _get_coordinates_within_range of a client class
    def test_translated_coords(self) -> None:
        """Test getting all coordinates at a given range from a translated hex."""
        coords = StarMap._get_coordinates_within_range(Coordinate(-1,-1,2), 1)
        self.assertEqual(len(coords), 6)
        self.assertTrue(Coordinate(0,-1,1) in coords) # axial hexes
        self.assertTrue(Coordinate(-1,0,1) in coords)
        self.assertTrue(Coordinate(-2,0,2) in coords)
        self.assertTrue(Coordinate(-2,-1,3) in coords)
        self.assertTrue(Coordinate(-1,-2,3) in coords)
        self.assertTrue(Coordinate(0,-2,2) in coords) # no edge hexes

    # pylint: disable=W0212
    # W0212: Access to a protected member _generate_new_system of a client class
    def test_generate_new_system(self) -> None:
        """Test generation of new hexes, either StarSystems or DeepSpace.

        The function output is random, so we can only test for sample
        sizes. We are guessing at a reasonable bound, but this test could
        occasionally fail nontheless.
        """
        worlds = []
        for _ in range(100):
            world = StarMap._generate_new_system(Coordinate(0,0,0))
            if world is not None:
                worlds.append(world)
        self.assertEqual(len(worlds), 100)

        systems = [s for s in worlds if isinstance(s, StarSystem)]
        self.assertTrue(len(systems) < 75)
        self.assertTrue(len(systems) > 25)

        for item in worlds:
            self.assertTrue(type(item) in [DeepSpace, StarSystem])

    def test_get_all_systems(self) -> None:
        """Test retrieval of all StarSystems from the fixture StarMap."""
        star_map1 = StarMapTestCase.star_map1
        systems = star_map1.get_all_systems()
        self.assertEqual(len(systems), 4)
        self.assertEqual(systems[0], StarSystemFactory.create("Aramis",
                                                              Coordinate(-1,1,0),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))
        self.assertEqual(systems[1], StarSystemFactory.create("Mithril",
                                                              Coordinate(0,-1,1),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))
        self.assertEqual(systems[2], StarSystemFactory.create("Yorbund",
                                                              Coordinate(0,0,0),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))
        self.assertEqual(systems[3], StarSystemFactory.create("Kinorb",
                                                              Coordinate(1,0,-1),
                                                              "A", 5, 5, 5, 5, 5, 5, 5))

    def test_pretty_coordinates(self) -> None:
        """Test conversion of absolute Traveller coordinates to a string."""
        star_map = StarMapTestCase.star_map1
        star_map.subsectors[(-1,0)]  = Subsector("LEFT", (-1,0))
        star_map.subsectors[(-1,-1)] = Subsector("UP LEFT", (-1,-1))
        star_map.subsectors[(0,-1)]  = Subsector("UP", (0,-1))

        result = star_map.pretty_coordinates(((1, 1), (0, 0)))
        self.assertEqual(result, "ORIGIN 0101")

        result = star_map.pretty_coordinates(((2, 1), (0, 0)))
        self.assertEqual(result, "ORIGIN 0201")

        result = star_map.pretty_coordinates(((8, 10), (0, 0)))
        self.assertEqual(result, "ORIGIN 0810")

        result = star_map.pretty_coordinates(((8, 1), (-1, 0)))
        self.assertEqual(result, "LEFT 0801")

        result = star_map.pretty_coordinates(((8, 10), (-1, -1)))
        self.assertEqual(result, "UP LEFT 0810")

        result = star_map.pretty_coordinates(((1, 10), (0, -1)))
        self.assertEqual(result, "UP 0110")

        # test randomly generated - only coordinates are predictable
        result = star_map.pretty_coordinates(((1, 1), (1, 1)))
        self.assertEqual(result[-4:], "0101")

        result = star_map.pretty_coordinates(((5, 7), (10, 6)))
        self.assertEqual(result[-4:], "0507")


class StarSystemFactoryTestCase(unittest.TestCase):
    """Tests StarSystemFactory class."""

    def test_generate(self) -> None:
        """Test random generation of StarSystems."""
        system = StarSystemFactory.generate(Coordinate(0,0,0))
        self.assertEqual(system.coordinate, Coordinate(0,0,0))

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

    def test_create(self) -> None:
        """Test creation of StarSystems by explicit parameters."""
        world = StarSystemFactory.create("Yorbund", Coordinate(0,0,0), "A", 8, 7, 5, 9, 5, 5, 10)

        self.assertTrue(isinstance(world, StarSystem))
        self.assertEqual(world.name, "Yorbund")
        self.assertEqual(world.coordinate, Coordinate(0,0,0))
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

class SubsectorTestCase(unittest.TestCase):
    """Tests Subsector class."""

    def test_from_string(self) -> None:
        """Test importing a Subsector from a string."""
        string = "(0, 0) - Regina"
        actual = subsector_from(string)
        expected = Subsector("Regina", (0,0))
        self.assertEqual(actual, expected)

        string = "(-1, 0) - Betelgeuse Marches"
        actual = subsector_from(string)
        expected = Subsector("Betelgeuse Marches", (-1,0))
        self.assertEqual(actual, expected)

        string = "Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "subsector data should have exactly two fields: 1")

        string = "(-1, 0) - Betelgeuse Marches - extra - stuff"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "subsector data should have exactly two fields: 4")

        string = "(0) - Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "coordinate should have exactly two integers: '(0,)'")

        string = "(0,0,0) - Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "coordinate should have exactly two integers: '(0, 0, 0)'")

        string = "(0,m) - Betelgeuse Marches"
        with self.assertRaises(ValueError) as context:
            _ = subsector_from(string)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")
