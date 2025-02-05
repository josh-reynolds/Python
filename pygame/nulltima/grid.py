import unittest
import math
import pygame
from pygame.locals import *
import game
import world

class Grid(game.Component):
    def __init__(self, size, pos, cell_width=32, cell_height=32):
        super().__init__(pos)
        self.width = size[0]
        self.height = size[1]
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.contents = [[Color('red') for x in range(self.width)] for x in range(self.height)]
        self.offset = (0,0)
        self.center = (self.width//2, self.height//2)
        self.edges = self._find_edges()

        self.world = world.World()
        self.file = 'large_world.txt'
        self.world.open_file(self.file)

        game.Game.level.grid = self
        game.Game.level.add_observer(self)
        self.on_notify(last_move=None, player_position=game.Game.level.player.pos)

    def update(self):
        self.world.update()

    def draw(self):
        for iy, row in enumerate(self.contents):
            for ix, cell in enumerate(row):
                grid_coord = (ix,iy)
                screen_coord = self.to_screen(grid_coord)
                # TO_DO: should only do this if cell type is SmartTerrain
                neighbors = self.count_matching_neighbors(self.to_world(grid_coord))
                image = self[grid_coord].get_image(neighbors)
                if self._is_occluded(grid_coord):
                    image = self.world.get_occluded().image
                game.Game.screen.blit(image, screen_coord)

    # TO_DO: think about edge conditions...
    def count_matching_neighbors(self, world_coord):
        current_terrain = self.world.get_cell(world_coord[0], world_coord[1])
        count = 0
        for direction in [(0,-1,1), (1,0,2), (0,1,4), (-1,0,8)]:
            neighbor_coord = (world_coord[0] + direction[0],
                              world_coord[1] + direction[1])
            if self.world.get_cell(neighbor_coord[0], neighbor_coord[1]) == current_terrain:
                count += direction[2]
        return count

    def __getitem__(self, index):
        return self.world.get_cell(index[1] + self.offset[1], 
                                   index[0] + self.offset[0])

    def _find_edges(self):
        edges = []
        for iy,row in enumerate(self.contents):
            for ix,cell in enumerate(row):
                if ix == 0 or iy == 0 or ix == self.width-1 or iy == self.height-1:
                    edges.append((ix,iy))
        return edges

    def spawnable(self):
        return [x for x in self.edges if self[x].is_passable]

    def on_notify(self, last_move, player_position):
        self.offset = (player_position[0] - self.center[0],
                       player_position[1] - self.center[1])

    def _is_occluded(self, coordinate):
        cells = self._bresenham(coordinate)
        for cell in cells:
            if self[cell].is_opaque:
                return True
        return False

    # assumes we are tracing a line to the center of the grid
    # since this consumes index coordinates, we have an origin in 
    # the top-left corner and are only dealing with one cartesian quadrant
    # (plus it's upside down) - may need to adjust, and possibly simplify.
    # starting with the full algorithm
    def _bresenham(self, coordinate):
        cells = []

        x = self.center[0]
        y = self.center[1]
        dx = coordinate[0] - x
        dy = coordinate[1] - y
        ax = 2 * abs(dx)
        ay = 2 * abs(dy)
        sx = math.copysign(1, dx)
        sy = math.copysign(1, dy)

        if ax > ay:
            d = ay - ax/2
            while True:
                if self._not_endpoint(x, y, coordinate[0], coordinate[1]):
                    cells.append((int(x), int(y)))
                if x == coordinate[0]:
                    return cells
                if d >= 0:
                    y = y + sy
                    d = d - ax
                x = x + sx
                d = d + ay
        else:
            d = ax - ay/2
            while True:
                if self._not_endpoint(x, y, coordinate[0], coordinate[1]):
                    cells.append((int(x), int(y)))
                if y == coordinate[1]:
                    return cells
                if d >= 0:
                    x = x + sx
                    d = d - ay
                y = y + sy
                d = d + ax

    def _not_endpoint(self, x1, y1, x2, y2):
        return (x1,y1) != (x2,y2) and (x1,y1) != (self.center[0], self.center[1])

    def from_world(self, coordinate):
        return (coordinate[0] - self.offset[0],
                coordinate[1] - self.offset[1])

    def to_world(self, coordinate):
        return (coordinate[0] + self.offset[0],
                coordinate[1] + self.offset[1])

    def to_screen(self, coordinate):
        return (coordinate[0] * self.cell_width + self.pos[0],
                coordinate[1] * self.cell_height + self.pos[1],
                self.cell_width,
                self.cell_height)

    def _on_grid(self, coordinate):
        grid_coord = self.from_world(coordinate)
        return (grid_coord[0] >= 0 and grid_coord[0] < self.width and
                grid_coord[1] >= 0 and grid_coord[1] < self.height)

    def can_view(self, coordinate):
        grid_coord = self.from_world(coordinate)
        return self._on_grid(coordinate) and not self._is_occluded(grid_coord)

    def is_vacant(self, coordinate):
        for monster in game.Game.level.monsters:
            if monster.pos == coordinate:
                return False
        return True

class GridTestCase(unittest.TestCase):
    def setUp(self):
        self.game = game.GameMock()
        game.Overworld()
        self.g = Grid(size=(3, 3), pos=(11, 9), cell_width=4, cell_height=3)
        self.g.world.contents = [[0, 0, 0, 0, 0],
                                [0, 1, 1, 1, 0],
                                [0, 1, 1, 1, 0],
                                [0, 1, 1, 1, 0],
                                [0, 0, 0, 0, 0]]

    def test_constructing_a_grid(self):
        self.assertEqual(self.g.width, 3)
        self.assertEqual(self.g.height, 3)
        self.assertEqual(self.g.pos, (11, 9))
        self.assertEqual(self.g.cell_width, 4)
        self.assertEqual(self.g.cell_height, 3)

    def test_coordinate_mapping_to_world(self):
        self.g.on_notify(None, (1,1))    # we need to move the player position now...
        self.assertEqual(self.g[2,2], self.g.world.get_cell(1,1))

    def test_coordinate_offset(self):
        self.g.offset = (1,1)

        self.assertEqual(self.g[1,1], self.g.world.terrains[1])

    #def test_moving_a_grid(self):
        #self.g.move(1,2)
#
        #self.assertEqual(self.g.offset, (1, 2))

    def test_converting_grid_coords_to_screen(self):
        grid_coord = (1, 1)
        coords = self.g.to_screen(grid_coord)

        self.assertEqual(coords[0], 15)
        self.assertEqual(coords[1], 12)
        self.assertEqual(coords[2], 4)
        self.assertEqual(coords[3], 3)

    #def test_move_check(self):
        #self.assertEqual(self.g.can_move(0,1), True)
        #self.assertEqual(self.g.can_move(1,0), True)
        #self.assertEqual(self.g.can_move(0,-1), False)
        #self.assertEqual(self.g.can_move(-1,0), False)

    def test_bresenham_calculation(self):
        g = Grid(size=(11, 11), pos=(5, 5), cell_width=5, cell_height=5)
        g.world.contents = [[0 for x in range(20)] for x in range(20)]

        b = g._bresenham((0,0))
        self.assertEqual(b, [(4,4), (3,3), (2,2), (1,1)])

        b = g._bresenham((10,10))
        self.assertEqual(b, [(6,6), (7,7), (8,8), (9,9)])

        b = g._bresenham((0,10))
        self.assertEqual(b, [(4,6), (3,7), (2,8), (1,9)])

        b = g._bresenham((10,0))
        self.assertEqual(b, [(6,4), (7,3), (8,2), (9,1)])

    def test_calculating_edge_cells(self):
        self.game = game.GameMock()
        game.Overworld()
        g = Grid(size=(5, 5), pos=(3, 3), cell_width=3, cell_height=3)

        e = g.edges
        self.assertEqual(e, [(0,0), (1,0), (2,0), (3,0), (4,0),
                             (0,1), (4,1),
                             (0,2), (4,2),
                             (0,3), (4,3),
                             (0,4), (1,4), (2,4), (3,4), (4,4)])

    def test_neighbor_count(self):
        self.g = Grid(size=(5, 5), pos=(1, 1), cell_width=1, cell_height=1)
        self.g.world.contents = [[ 0,  6, 10,  6, 10],
                                 [ 6,  1, 10,  1,  6],
                                 [10, 10, 10, 10, 10],
                                 [ 6,  1, 10,  1,  6],
                                 [ 0,  6, 10,  6,  0]]
        self.g.on_notify(None, (2,2))    # we need to move the player position now...

        self.assertEqual(self.g.count_matching_neighbors((2,2)), 15)
        self.assertEqual(self.g.count_matching_neighbors((1,2)), 10)
        self.assertEqual(self.g.count_matching_neighbors((3,2)), 10)
        self.assertEqual(self.g.count_matching_neighbors((2,1)), 5)
        self.assertEqual(self.g.count_matching_neighbors((2,3)), 5)
        self.assertEqual(self.g.count_matching_neighbors((4,0)), 0)
        self.assertEqual(self.g.count_matching_neighbors((2,0)), 4)
        self.assertEqual(self.g.count_matching_neighbors((0,2)), 2)
        self.assertEqual(self.g.count_matching_neighbors((4,2)), 8)
        self.assertEqual(self.g.count_matching_neighbors((2,4)), 1)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
