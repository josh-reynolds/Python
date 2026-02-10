"""Contains tests for the intersections functions."""
import unittest
from intersections import segments_intersect, rect_segment_intersects

class SegmentIntersectionTestCase(unittest.TestCase):
    """Tests intersection of line segments."""

    def test_intersections(self) -> None:
        """Tests simple line segment intersection."""
        pass

    #def test_game_ctor(self) -> None:
        #"""Tests construction of a Game object."""
        #game = Game()
        #self.assertFalse(game.running)
        #self.assertTrue(isinstance(game.screen, MenuScreen))
#
    #@unittest.skip("test has side effects: input & printing")
    #def test_get_input(self) -> None:
        #"""Test requesting input from the controller."""
        #game = Game()
#
        #result2 = game.get_input('', "No constraint test.")
#
        #result2 = game.get_input('confirm', "Confirmation test.")
        #self.assertTrue(result2 in ['y', 'n'])
#
        #result3 = game.get_input('int', "Integer input test.")
        #self.assertTrue(isinstance(result3, int))
