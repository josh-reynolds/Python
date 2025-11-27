"""Contains tests for the star_system_factory module."""
import unittest
from src.coordinate import Coordinate
from src.star_system import StarSystem
import src.star_system_factory

class StarSystemFactoryTestCase(unittest.TestCase):
    """Tests StarSystemFactory module."""

    def test_generate(self) -> None:
        """Test random generation of StarSystems."""
        system = src.star_system_factory.generate(Coordinate(0,0,0))
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
        world = src.star_system_factory.create("Yorbund", Coordinate(0,0,0),
                                               "A", 8, 7, 5, 9, 5, 5, 10)

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
