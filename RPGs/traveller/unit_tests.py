import unittest

def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromName('calendar'))
    test_suite.addTests(loader.loadTestsFromName('cargo'))
    test_suite.addTests(loader.loadTestsFromName('financials'))
    test_suite.addTests(loader.loadTestsFromName('ship'))
    test_suite.addTests(loader.loadTestsFromName('star_system'))
    test_suite.addTests(loader.loadTestsFromName('utilities'))
    return test_suite

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
