import unittest

def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromName('calendar'))
    suite.addTests(loader.loadTestsFromName('cargo'))
    suite.addTests(loader.loadTestsFromName('financials'))
    suite.addTests(loader.loadTestsFromName('ship'))
    suite.addTests(loader.loadTestsFromName('star_system'))
    suite.addTests(loader.loadTestsFromName('utilities'))
    return suite

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())



