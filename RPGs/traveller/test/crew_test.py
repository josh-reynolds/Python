"""Contains tests for the crew module."""
import unittest
from src.credits import Credits
from src.crew import Pilot, Engineer, Medic, Steward

class PilotTestCase(unittest.TestCase):
    """Tests Pilot class."""

    def test_salary(self) -> None:
        """Test retrieval of Pilot salary value."""
        self.assertEqual(Pilot(1).salary(), Credits(6000))
        self.assertEqual(Pilot(2).salary(), Credits(6600))
        self.assertEqual(Pilot(3).salary(), Credits(7200))

class EngineerTestCase(unittest.TestCase):
    """Tests Engineer class."""

    def test_salary(self) -> None:
        """Test retrieval of Engineer salary value."""
        self.assertEqual(Engineer(1).salary(), Credits(4000))
        self.assertEqual(Engineer(2).salary(), Credits(4400))
        self.assertEqual(Engineer(3).salary(), Credits(4800))

class MedicTestCase(unittest.TestCase):
    """Tests Medic class."""

    def test_salary(self) -> None:
        """Test retrieval of Medic salary value."""
        self.assertEqual(Medic(1).salary(), Credits(2000))
        self.assertEqual(Medic(2).salary(), Credits(2200))
        self.assertEqual(Medic(3).salary(), Credits(2400))

class StewardTestCase(unittest.TestCase):
    """Tests Steward class."""

    def test_salary(self) -> None:
        """Test retrieval of Steward salary value."""
        self.assertEqual(Steward(1).salary(), Credits(3000))
        self.assertEqual(Steward(2).salary(), Credits(3300))
        self.assertEqual(Steward(3).salary(), Credits(3600))
