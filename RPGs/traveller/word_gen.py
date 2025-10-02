import unittest

def get_name():
    return "Test"

class WordGenTestCase(unittest.TestCase):
    def test_word_gen(self):
        self.assertEqual(get_name(), "Test")

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
