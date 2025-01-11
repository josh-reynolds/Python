import unittest

def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromName('grid'))
    suite.addTests(loader.loadTestsFromName('player'))
    suite.addTests(loader.loadTestsFromName('world'))
    return suite

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())



