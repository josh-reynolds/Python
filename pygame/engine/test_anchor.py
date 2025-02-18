import unittest
from engine import Actor

class ActorTestCase(unittest.TestCase):
    def test_constructing_an_actor(self):
        a = Actor('blank', (100,100))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('center','center'))
        self.assertEqual(a.anchor_value, (0,0))
        self.assertEqual(a.rect.topleft, (100,100))
        self.assertEqual(a.rect.left, 100)
        self.assertEqual(a.rect.top, 100)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_a_larger_actor(self):
        a = Actor('box', (100,100))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('center','center'))
        self.assertEqual(a.anchor_value, (16,16))
        self.assertEqual(a.rect.topleft, (84,84))
        self.assertEqual(a.rect.left, 84)
        self.assertEqual(a.rect.top, 84)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_a_very_large_actor(self):
        a = Actor('big_box', (100,100))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('center','center'))
        self.assertEqual(a.anchor_value, (64,64))
        self.assertEqual(a.rect.topleft, (36,36))
        self.assertEqual(a.rect.left, 36)
        self.assertEqual(a.rect.top, 36)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_topleft_anchor(self):
        a = Actor('box', (100,100), anchor=('left','top'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('left','top'))
        self.assertEqual(a.anchor_value, (0,0))
        self.assertEqual(a.rect.topleft, (100,100))
        self.assertEqual(a.rect.left, 100)
        self.assertEqual(a.rect.top, 100)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_a_very_large_actor_with_topleft_anchor(self):
        a = Actor('big_box', (100,100), anchor=('left','top'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('left','top'))
        self.assertEqual(a.anchor_value, (0,0))
        self.assertEqual(a.rect.topleft, (100,100))
        self.assertEqual(a.rect.left, 100)
        self.assertEqual(a.rect.top, 100)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_top_anchor(self):
        a = Actor('box', (100,100), anchor=('center','top'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('center','top'))
        self.assertEqual(a.anchor_value, (16,0))
        self.assertEqual(a.rect.topleft, (84,100))
        self.assertEqual(a.rect.left, 84)
        self.assertEqual(a.rect.top, 100)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_topright_anchor(self):
        a = Actor('box', (100,100), anchor=('right','top'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('right','top'))
        self.assertEqual(a.anchor_value, (32,0))
        self.assertEqual(a.rect.topleft, (68,100))
        self.assertEqual(a.rect.left, 68)
        self.assertEqual(a.rect.top, 100)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_left_anchor(self):
        a = Actor('box', (100,100), anchor=('left','center'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('left','center'))
        self.assertEqual(a.anchor_value, (0,16))
        self.assertEqual(a.rect.topleft, (100,84))
        self.assertEqual(a.rect.left, 100)
        self.assertEqual(a.rect.top, 84)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_right_anchor(self):
        a = Actor('box', (100,100), anchor=('right','center'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('right','center'))
        self.assertEqual(a.anchor_value, (32,16))
        self.assertEqual(a.rect.topleft, (68,84))
        self.assertEqual(a.rect.left, 68)
        self.assertEqual(a.rect.top, 84)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_bottomleft_anchor(self):
        a = Actor('box', (100,100), anchor=('left','bottom'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('left','bottom'))
        self.assertEqual(a.anchor_value, (0,32))
        self.assertEqual(a.rect.topleft, (100,68))
        self.assertEqual(a.rect.left, 100)
        self.assertEqual(a.rect.top, 68)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_bottom_anchor(self):
        a = Actor('box', (100,100), anchor=('center','bottom'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('center','bottom'))
        self.assertEqual(a.anchor_value, (16,32))
        self.assertEqual(a.rect.topleft, (84,68))
        self.assertEqual(a.rect.left, 84)
        self.assertEqual(a.rect.top, 68)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_constructing_with_bottomright_anchor(self):
        a = Actor('box', (100,100), anchor=('right','bottom'))
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('right','bottom'))
        self.assertEqual(a.anchor_value, (32,32))
        self.assertEqual(a.rect.topleft, (68,68))
        self.assertEqual(a.rect.left, 68)
        self.assertEqual(a.rect.top, 68)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_changing_to_a_larger_image(self):
        a = Actor('box', (100,100), anchor=('center','center'))
        a.image = 'big_box'
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('center','center'))
        self.assertEqual(a.anchor_value, (64,64))
        self.assertEqual(a.rect.topleft, (36,36))
        self.assertEqual(a.rect.left, 36)
        self.assertEqual(a.rect.top, 36)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

    def test_changing_to_a_smaller_image(self):
        a = Actor('big_box', (100,100), anchor=('center','center'))
        a.image = 'box'
        self.assertEqual(a.pos, (100,100))
        self.assertEqual(a.anchor, ('center','center'))
        self.assertEqual(a.anchor_value, (16,16))
        self.assertEqual(a.rect.topleft, (84,84))
        self.assertEqual(a.rect.left, 84)
        self.assertEqual(a.rect.top, 84)
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 100)

# --------------------------------------------------
if __name__ == '__main__':
    unittest.main()
