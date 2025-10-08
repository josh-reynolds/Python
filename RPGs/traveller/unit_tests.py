"""Unit tests for the Traveller trading game."""
import unittest

def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromName('calendar_test'))
    test_suite.addTests(loader.loadTestsFromName('cargo_test'))
    test_suite.addTests(loader.loadTestsFromName('financials_test'))
    test_suite.addTests(loader.loadTestsFromName('ship_test'))
    test_suite.addTests(loader.loadTestsFromName('star_map_test'))
    test_suite.addTests(loader.loadTestsFromName('star_system_test'))
    test_suite.addTests(loader.loadTestsFromName('traveller_test'))
    test_suite.addTests(loader.loadTestsFromName('utilities_test'))
    test_suite.addTests(loader.loadTestsFromName('word_gen_test'))
    return test_suite

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
