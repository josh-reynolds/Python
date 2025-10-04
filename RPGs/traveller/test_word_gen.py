"""Contains tests for the word_gen module."""
import unittest
from word_gen import get_world_name

class WordGenTestCase(unittest.TestCase):
    """Tests word generation functions."""

    def test_get_world_name_strips_newline(self):
        self.assertNotEqual(get_world_name()[-1], "\n")

# -------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
