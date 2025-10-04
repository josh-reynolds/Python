"""Contains classes to create and manage a Traveller star map.

StarSystemFactory - builds StarSystem objects using the Traveller '77 rules.
StarMap - represents a map of StarSystems laid out on a hexagonal grid.
"""
from random import randint
from word_gen import get_world_name
from star_system import StarSystem, DeepSpace
from utilities import die_roll, constrain

# in the three-axis system:
#  * the three coordinates sum to zero
#  * the distance from origin is max(|x|, |y|, |z|)

# the origin is of course (0,0,0)
# the six surrounding coordinates are:
# (0, 1, -1), (0, -1, 1)
# (1, 0, -1), (-1, 0, 1)
# (1, -1, 0), (-1, 1, 0)

# the axial rows are straightforward. one
# coordinate is zero, and the other two are
# +x/-x. So:
# (0,x,-x) & (0,-x,x)
# (x,0,-x) & (-x,0,x)
# (x,-x,0) & (-x,x,0)

# A ring of hexes at a given distance from a
# central origin hex contains six axial hexes
# and a variable number of edge hexes. There
# are (range-1)*6 such hexes, so 0 at range 1,
# 6 at range 2, 12 at range 3, etc. So the total
# number of hexes in a ring are equal to:
#   6 + (range-1)*6.

# As noted above, axial hexes are trivial to
# figure out. Just all the valid variations of
# +range, -range, and zero (one of each per coord).

# Edge hexes are trickier. They are grouped into
# six 'pie slices,' each bounded by two different
# axes. If we call the axes red, blue, green, then
# the slices are:
#   +blue, +red     (-green)
#   -red, -green    (+blue)
#   +blue, +green   (-red)
#   -blue, -red     (+green)
#   +red, +green    (-blue)
#   -blue, -green   (+red)
#
# (Each slice also sits entirely to one side of the
#  third 'non-bounding' axis, as noted in parens above.)
#
# The edge coordinates at a given range are the sum of
# the corresponding axial hexes along that span, just
# like with Cartesian coordinates. It's the same sort
# of transform - go over 3 on the x-axis, and up 2 on
# the y-axis, and arrive at (3,2). Instead we would
# go over 3 on the blue-axis, and up 2 on the red-axis,
# and arrive at (3,2,-5). The third coordinate is
# really just a checksum and can be calculated given
# the other two, since sum(a,b,c) = 0. Tricky bit is this
# hex is _five_ away from the origin, so arriving at it
# from just the range value is tricky.

# An alternate strategy:
# * the complete set of coordinates at a given range x
#   (including invalid coordinates) is given by:
#   [(a,b,c) for a in range(-x,x+1)
#            for b in range(-x,x+1)
#            for c in range(-x,x+1)]

# * the length of this list is (2x+1)^3, so
#   27 (3 cubed) at range 1, 125 (5 cubed) at range 2, etc.
#
# * we can then filter out the invalid members with a
#   simple test, and voila! There's the list at range x.
#
#   [a for a in full_list if sum(a)==0]
#   a.remove((0,0,0))                   # probably also want
#                                       # to drop the origin...
#
# Then, if we want to find hexes around some arbitrary
# point, we just translate everything to that new origin
# (by adding the new origin to every coordinate of course).

# World generation from Traveller '77 Book 3 pp. 4-12
# constraints based on the tables, though the dice throws
# in the text can produce values outside this range in
# some cases
class StarSystemFactory:
    """Builds StarSystem objects using the Traveller '77 rules."""

    @classmethod
    def create(cls, name, coordinate, starport, size, atmosphere,
               hydrographics, population, government, law, tech, gas_giant=True):
        return StarSystem(name, coordinate, starport, size, atmosphere,
                          hydrographics, population, government, law,
                          tech, gas_giant)

    @classmethod
    def generate(cls, coordinate):
        name = get_world_name()

        roll = die_roll() + die_roll()
        if roll <= 4:
            starport = "A"
        elif roll <= 6:
            starport = "B"
        elif roll <= 8:
            starport = "C"
        elif roll <= 9:
            starport = "D"
        elif roll <= 11:
            starport = "E"
        else:
            starport = "X"

        die_modifier = -2
        size = die_roll() + die_roll() + die_modifier

        die_modifier = size -7
        atmosphere = constrain(die_roll() + die_roll() + die_modifier,
                               0, 12)
        if size == 0:
            atmosphere = 0

        die_modifier = size - 7
        if atmosphere <= 1 or atmosphere > 9:
            die_modifier -= 4
        hydrographics = constrain(die_roll() + die_roll() + die_modifier,
                                  0,10)
        if size <= 1:
            hydrographics = 0

        die_modifier = -2
        population = die_roll() + die_roll() + die_modifier

        die_modifier = population - 7
        government = constrain(die_roll() + die_roll() + die_modifier,
                               0,13)

        die_modifier = government - 7
        law = constrain(die_roll() + die_roll() + die_modifier,
                               0,9)

        if starport == "A":
            die_modifier = 6
        elif starport == "B":
            die_modifier = 4
        elif starport == "C":
            die_modifier = 2
        elif starport == "X":
            die_modifier = -2
        else:
            die_modifier = 0

        if size in (0, 1):
            die_modifier += 2
        if size in (2, 3, 4):
            die_modifier += 1

        if atmosphere in (0, 1, 2, 3, 10, 11, 12):
            die_modifier += 1

        if hydrographics == 9:
            die_modifier += 1
        if hydrographics == 10:
            die_modifier += 2

        if population in (1, 2, 3, 4, 5):
            die_modifier += 1
        if population == 9:
            die_modifier += 2
        if population == 10:
            die_modifier += 4

        if government in (0, 5):
            die_modifier += 1
        if government == 13:
            die_modifier -= 2

        tech = constrain(die_roll() + die_modifier, 0, 18)

        gas_giant = bool(die_roll() + die_roll() < 10)

        return StarSystem(name, coordinate, starport, size, atmosphere,
                          hydrographics, population, government, law, tech, gas_giant)

class StarMap:
    """Represents a map of StarSystems laid out on a hexagonal grid."""

    def __init__(self, systems):
        self.systems = systems
        for key in self.systems.keys():
            if not StarMap.valid_coordinate(key):
                raise ValueError(f"Invalid three-axis coordinate: {key}")

    def get_systems_within_range(self, origin, distance):
        result = []
        for coord in StarMap.get_coordinates_within_range(origin, distance):
            if coord in self.systems:
                if isinstance(self.systems[coord], StarSystem):
                    result.append(self.systems[coord])
            else:
                system = StarMap.generate_new_system(coord)
                self.systems[coord] = system
                if isinstance(system, StarSystem):
                    result.append(system)
        return result

    def get_system_at_coordinate(self, coordinate):
        return self.systems.get(coordinate, StarMap.generate_new_system(coordinate))

    def get_all_systems(self):
        systems = [s for i,(k,s) in enumerate(self.systems.items()) if
                   isinstance(s, StarSystem)]
        systems = sorted(systems, key=lambda system: system.coordinate)
        return systems

    @classmethod
    def generate_new_system(cls, coordinate):
        if randint(1,6) >= 4:
            return StarSystemFactory.generate(coordinate)
        return DeepSpace(coordinate)

    @classmethod
    def distance_between(cls, first, second):
        transformed = (second[0]-first[0],
                       second[1]-first[1],
                       second[2]-first[2])
        return max(abs(transformed[0]),
                   abs(transformed[1]),
                   abs(transformed[2]))

    @classmethod
    def valid_coordinate(cls, coord):
        return sum(coord) == 0

    # TO_DO: should we default origin param to (0,0,0)?
    @classmethod
    def get_coordinates_within_range(cls, origin, radius):
        full_list = StarMap.get_all_coords(radius)

        filtered = [a for a in full_list if sum(a)==0]
        filtered.remove((0,0,0))

        translated = [(f[0] + origin[0],
                       f[1] + origin[1],
                       f[2] + origin[2]) for f in filtered]

        return translated

    @classmethod
    def get_all_coords(cls, radius):
        span = range(-radius, radius+1)
        return [(a,b,c) for a in span
                        for b in span
                        for c in span]
