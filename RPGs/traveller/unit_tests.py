"""Unit tests for the Traveller trading game."""
import unittest

def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromName('test_calendar'))
    test_suite.addTests(loader.loadTestsFromName('test_cargo'))
    test_suite.addTests(loader.loadTestsFromName('test_financials'))
    test_suite.addTests(loader.loadTestsFromName('test_ship'))
    test_suite.addTests(loader.loadTestsFromName('star_map'))
    test_suite.addTests(loader.loadTestsFromName('star_system'))
    test_suite.addTests(loader.loadTestsFromName('utilities'))
    test_suite.addTests(loader.loadTestsFromName('word_gen'))
    return test_suite

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
