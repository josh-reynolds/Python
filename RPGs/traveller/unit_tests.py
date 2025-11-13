"""Unit tests for the Traveller trading game."""
import unittest

def suite():
    """Create a suite of test cases."""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.discover('.', '*_test.py'))
    return test_suite

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
