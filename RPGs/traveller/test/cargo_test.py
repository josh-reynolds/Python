"""Contains tests for the cargo module."""
import unittest
from typing import Sequence
from test.mock import SystemMock
from src.baggage import Baggage
from src.cargo import Cargo, cargo_from
from src.cargo_depot import cargo_hold_from
from src.coordinate import Coordinate
from src.financials import Credits
from src.freight import Freight
from src.star_system import StarSystem
from src.utilities import dictionary_from

class CargoTestCase(unittest.TestCase):
    """Tests Cargo class."""

    def test_cargo_quantity(self) -> None:
        """Test whether cargo quantity is determined correctly."""
        cargo1 = Cargo("Foo", '10', Credits(10), 1, {}, {})
        self.assertEqual(cargo1.quantity, 10)

        cargo2 = Cargo("Bar", "1Dx1", Credits(10), 1, {}, {})
        self.assertGreater(cargo2.quantity, 0)
        self.assertLess(cargo2.quantity, 7)

        cargo3 = Cargo("Baz", "1Dx10", Credits(10), 1, {}, {})
        self.assertEqual(cargo3.quantity % 10, 0)
        self.assertGreater(cargo3.quantity, 9)
        self.assertLess(cargo3.quantity, 61)

    def test_cargo_quantity_string(self) -> None:
        """Test the string representation of cargo quantity."""
        cargo1 = Cargo("Foo", '1', Credits(10), 1, {}, {})
        self.assertEqual(cargo1.quantity_string(1), "1 ton")
        self.assertEqual(cargo1.quantity_string(5), "5 tons")

        cargo2 = Cargo("Bar", '1', Credits(10), 5, {}, {})
        self.assertEqual(cargo2.quantity_string(1), "1 (5 tons/item)")

    def test_cargo_tonnage(self) -> None:
        """Test whether cargo tonnage is calculated correctly."""
        cargo1 = Cargo("Foo", '1', Credits(10), 1, {}, {})
        self.assertEqual(cargo1.tonnage, 1)

        cargo2 = Cargo("Bar", '1', Credits(10), 5, {}, {})
        self.assertEqual(cargo2.tonnage, 5)

        cargo3 = Cargo("Baz", '20', Credits(10), 1, {}, {})
        self.assertEqual(cargo3.tonnage, 20)

        cargo4 = Cargo("Boo", '20', Credits(10), 10, {}, {})
        self.assertEqual(cargo4.tonnage, 200)

    def test_cargo_string(self) -> None:
        """Test a Cargo's string representation."""
        cargo1 = Cargo("Foo", '1', Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo1}", "Foo - 1 ton - 10 Cr/ton")

        cargo2 = Cargo("Bar", '5', Credits(10), 1, {}, {})
        self.assertEqual(f"{cargo2}", "Bar - 5 tons - 10 Cr/ton")

        cargo3 = Cargo("Baz", '5', Credits(10), 5, {}, {})
        self.assertEqual(f"{cargo3}", "Baz - 5 (5 tons/item) - 10 Cr/item")

        # pylint: disable=R0903
        # R0903: Too few public methods (0/2)
        class Location(StarSystem):
            """Mocks a location interface for testing."""

            # pylint: disable=W0231
            # W0231: __init__ method from base class 'StarSystem' is not called
            def __init__(self, name: str) -> None:
                self.name = name

        location = Location("Uranus")
        cargo4 = Cargo("Boo", '100', Credits(10), 1, {}, {}, location)
        self.assertEqual(f"{cargo4}", "Boo - 100 tons - 10 Cr/ton (Uranus)")

    def test_cargo_from(self) -> None:
        """Test importing Cargo from a parsed string."""
        source_1 = SystemMock("Uranus")
        source_1.coordinate = Coordinate(1,0,-1)
        source_2 = SystemMock("Jupiter")
        source_2 .coordinate = Coordinate(0,0,0)
        systems = {Coordinate(0,0,0) : source_2 ,
                   Coordinate(1,0,-1) : source_1}

        actual = cargo_from("Meat", 10, None, systems)
        expected = Cargo("Meat", "10", Credits(1500), 1,
                         dictionary_from("{Ag:-2,Na:2,In:3}"),
                         dictionary_from("{Ag:-2,In:2,Po:1}"))
        self.assertEqual(actual, expected)
        self.assertEqual(actual.tonnage, expected.tonnage)

        actual = cargo_from("Mechanical Parts", 15, None, systems)
        expected = Cargo("Mechanical Parts", "15", Credits(75000), 1,
                         dictionary_from("{In:-5,Ri:-3}"),
                         dictionary_from("{Ag:2,Ni:3}"))
        self.assertEqual(actual, expected)
        self.assertEqual(actual.tonnage, expected.tonnage)

        actual = cargo_from("Computers", 3, None, systems)
        expected = Cargo("Computers", "3", Credits(10000000), 2,
                         dictionary_from("{In:-2,Ri:-2}"),
                         dictionary_from("{Ag:-3,Ni:2,Po:1}"))
        self.assertEqual(actual, expected)
        self.assertEqual(actual.tonnage, expected.tonnage)

        actual = cargo_from("Tools", 7, "(1,0,-1)", systems)
        expected = Cargo("Tools", "7", Credits(10000), 1,
                         dictionary_from("{In:-3,Ri:-2,Po:3}"),
                         dictionary_from("{In:-2,Ri:-1,Po:3}"),
                         source_1)
        self.assertEqual(actual, expected)
        self.assertEqual(actual.tonnage, expected.tonnage)

        with self.assertRaises(ValueError) as context:
            _ = cargo_from("Monkeys", 100, None, systems)
        self.assertEqual(f"{context.exception}",
                         "cargo not found in the cargo table: 'Monkeys'")

        with self.assertRaises(ValueError) as context:
            actual = cargo_from("Tools", 0, None, systems)
        self.assertEqual(f"{context.exception}",
                         "quantity must be a positive number: '0'")

        with self.assertRaises(ValueError) as context:
            actual = cargo_from("Tools", -1, None, systems)
        self.assertEqual(f"{context.exception}",
                         "quantity must be a positive number: '-1'")

        with self.assertRaises(ValueError) as context:
            actual = cargo_from("Tools", 'm', None, systems)    #type: ignore[arg-type]
        self.assertEqual(f"{context.exception}",
                         "quantity must be an integer: 'm'")

        with self.assertRaises(ValueError) as context:
            _ = cargo_from("Tools", 1, "(1, -1, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(1, -1, 0)'")

        with self.assertRaises(ValueError) as context:
            _ = cargo_from("Tools", 1, "(m, -1, 0)", systems)
        self.assertEqual(f"{context.exception}",
                         "invalid literal for int() with base 10: 'm'")

        with self.assertRaises(ValueError) as context:
            _ = cargo_from("Tools", 1, "(1, 1, 1)", systems)
        self.assertEqual(f"{context.exception}",
                         "string is not a valid 3-axis coordinate "
                         + "- should sum to zero: '(1, 1, 1)'")

    def test_encode(self) -> None:
        """Test exporting a Cargo object to a string."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        cargo = Cargo("Meat", "10", Credits(1500), 1,
                         dictionary_from("{Ag:-2,Na:2,In:3}"),
                         dictionary_from("{Ag:-2,In:2,Po:1}"),
                         source
                      )

        actual = cargo.encode()
        expected = "Cargo - Meat - 10 - (1, 0, -1)"
        self.assertEqual(actual, expected)

        cargo = Cargo("Meat", "10", Credits(1500), 1,
                         dictionary_from("{Ag:-2,Na:2,In:3}"),
                         dictionary_from("{Ag:-2,In:2,Po:1}")
                      )

        actual = cargo.encode()
        expected = "Cargo - Meat - 10 - None"
        self.assertEqual(actual, expected)


# pylint: disable=R0915
# R0915 Too many statements (52/50)
class CargoHoldTestCase(unittest.TestCase):
    """Tests populating a cargo hold from saved JSON data."""

    def test_cargo_hold_from(self) -> None:
        """Test importing a list of cargo hold items from JSON string data."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        alternate = SystemMock("Mars")
        alternate.coordinate = Coordinate(-1,0,1)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source,
                   Coordinate(-1,0,1) : alternate}

        data = ["Baggage - (1, 0, -1) - (0, 0, 0)"]
        actual = cargo_hold_from(data, systems)
        expected: Sequence[Freight | Cargo] = [Baggage(source, destination)]
        self.assertEqual(actual, expected)

        data = ["Freight - 10 - (1, 0, -1) - (0, 0, 0)"]
        actual = cargo_hold_from(data, systems)
        expected = [Freight(10, source, destination)]
        self.assertEqual(actual, expected)

        data = ["Cargo - Meat - 10 - None"]
        actual = cargo_hold_from(data, systems)
        expected = [Cargo("Meat", "10", Credits(1500), 1,
                          dictionary_from("{Ag:-2,Na:2,In:3}"),
                          dictionary_from("{Ag:-2,In:2,Po:1}"))]
        self.assertEqual(actual, expected)

        data = ["Baggage - (1, 0, -1) - (0, 0, 0)",
                "Freight - 10 - (1, 0, -1) - (0, 0, 0)",
                "Cargo - Meat - 10 - None"]
        actual = cargo_hold_from(data, systems)
        expected = [Baggage(source, destination),
                    Freight(10, source, destination),
                    Cargo("Meat", "10", Credits(1500), 1,
                          dictionary_from("{Ag:-2,Na:2,In:3}"),
                          dictionary_from("{Ag:-2,In:2,Po:1}"))]
        self.assertEqual(actual, expected)

        data = ["Freight - m - (1, 0, -1) - (0, 0, 0)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "invalid literal for int() with base 10: 'm'")

        data = ["Freight - 0 - (1, 0, -1) - (0, 0, 0)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "tonnage must be a positive number: '0'")

        data = ["Cargo - Meat - m - None"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "invalid literal for int() with base 10: 'm'")

        data = ["Cargo - Meat - -1 - None"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "quantity must be a positive number: '-1'")

        data = ["Monkeys - Meat - 100 - None"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "unknown hold content type: 'Monkeys'")

        data = ["Freight - 5 - (1, 0, -1) - (0, 0, 0)",
                "Baggage - (1, 0, -1) - (0, 0, 0)",
                "Freight - 10 - (1, 0, -1) - (-1, 0, 1)",
                "Freight - 15 - (1, 0, -1) - (0, 0, 0)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                          "more than one destination in saved "
                          + "data: '{'(0, 0, 0)', '(-1, 0, 1)'}'")

        data = ["Freight - 5 - (1, 0, -1) - (2, 0, -2)"]
        with self.assertRaises(ValueError) as context:
            _ = cargo_hold_from(data, systems)
        self.assertEqual(f"{context.exception}",
                         "coordinate not found in systems list: '(2, 0, -2)'")

    def test_cargo_hold_from_encode(self) -> None:
        """Test compatibility of *.encode() and cargo_hold_from()."""
        source = SystemMock("Uranus")
        source.coordinate = Coordinate(1,0,-1)
        destination = SystemMock("Jupiter")
        destination.coordinate = Coordinate(0,0,0)
        alternate = SystemMock("Mars")
        alternate.coordinate = Coordinate(-1,0,1)
        systems = {Coordinate(0,0,0) : destination,
                   Coordinate(1,0,-1) : source,
                   Coordinate(-1,0,1) : alternate}

        data = [Baggage(source, destination).encode(),
                Freight(10, source, destination).encode(),
                Cargo("Meat", "10", Credits(1500), 1,
                      dictionary_from("{Ag:-2,Na:2,In:3}"),
                      dictionary_from("{Ag:-2,In:2,Po:1}")).encode()]
        actual = cargo_hold_from(data, systems)
        expected = [Baggage(source, destination),
                    Freight(10, source, destination),
                    Cargo("Meat", "10", Credits(1500), 1,
                          dictionary_from("{Ag:-2,Na:2,In:3}"),
                          dictionary_from("{Ag:-2,In:2,Po:1}"))]
        self.assertEqual(actual, expected)
