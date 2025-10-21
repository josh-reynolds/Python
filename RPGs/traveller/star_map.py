"""Contains classes to create and manage a Traveller star map.

StarSystemFactory - builds StarSystem objects using the Traveller '77 rules.
StarMap - represents a map of StarSystems laid out on a hexagonal grid.
"""
from random import randint
from typing import Dict, List, Tuple, cast
from word_gen import get_world_name
from star_system import StarSystem, DeepSpace, UWP, Hex
from utilities import die_roll, constrain, Coordinate

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

# Converting to Traveller coordinates from 3-axis
# -----------------------------------------------
# As noted elsewhere, Traveller 77 uses an 8x10 grid of
# hexes, called a 'subsector.' Each hex is assigned a
# coordinate by row and column, as RRCC. So coordinates
# range from 0101 to 0810.
#
# Later game editions expanded this to a 'sector,'
# comprised of sixteen subsectors in a 4x4 grid. Initially
# worlds were still referenced by subsector coordinates,
# with the name of the subsector to distinguish. Later
# they started using coordinates based on the 32x40
# arrangement in the sector, so coordinates could now
# range from 0101 to 3240.
#
# For conversion, there are a few hurdles to cross:
#
# * Column number is easy. It maps directly to one of
#   the 3-axis values. Arbitrary. My hand-drawn version
#   I've been using to figure this out happens to use
#   the second value as the column offset.
# * Row number needs calculation. I have another project
#   where I figured this out; will crib if the derivation
#   doesn't come back to me easily.
# * Then need to address subsectors and sectors. First
#   as entities in their own right. I suppose eventually
#   I'll want to formalize them here, at a minimum for
#   any export functionality (and possibly import too),
#   but maybe make them visible in-game too.
# * But second, the impact on coordinates. Do we convert
#   to 8x10 or 32x40 values? And how do we handle crossing
#   boundaries?
# * Of course there will need to be some base offset. Where
#   is (0,0,0) located on the sector/subsector map?
#
# For the first steps, let's place the origin in the middle
# of a sector, so at 1620. That way we don't have to worry
# about boundaries just yet.
#
# ( 3, 0,-3)   0603  ( 0,-3)
# ( 2, 0,-2)   0604  ( 0,-2)
# ( 1, 0,-1)   0605  ( 0,-1)
# ( 0, 0, 0)   0606  ( 0, 0)
# (-1, 0, 1)   0607  ( 0, 1)
# (-2, 0, 2)   0608  ( 0, 2)
# (-3, 0, 3)   0609  ( 0, 3)
#
# ( 3,-1,-2)   0504  (-1,-2)
# ( 2,-1,-1)   0505  (-1,-1)
# ( 1,-1, 0)   0506  (-1, 0)
# ( 0,-1, 1)   0507  (-1, 1)
# (-1,-1, 2)   0508  (-1, 2)
# (-2,-1, 3)   0509  (-1, 3)
# (-3,-1, 4)   0510  (-1, 4)
#
# ( 3, 1,-4)   0703  ( 1,-3)
# ( 2, 1,-3)   0704  ( 1,-2)
# ( 1, 1,-2)   0705  ( 1,-1)
# ( 0, 1,-1)   0706  ( 1, 0)
# (-1, 1, 0)   0707  ( 1, 1)
# (-2, 1, 1)   0708  ( 1, 2)
# (-3, 1, 2)   0709  ( 1, 3)
#
# Transcribing from a physical map (above), and I think this is
# the formula:
#
# * Column offset = second 3-axis value
# * If column offset < 1, row offset = third 3-axis value
# * If column offset >= 1, row offset = -first 3-axis value
#
# Let's try it out...
# OK, test drove an implementation below, and it works according
# to the sample above... but grabbing some other coordinates off
# the map for additional verification, and we have issues. I have
# sneaking suspicion the location of the coordinate within the
# six 3-axis sectors holds the solution.
#
# Additional test cases seem to corroborate. Taking the six
# 'spine' hexes out from the origin, four are OK, implying +/-
# sectors match my algorithm. But the two sectors parallel
# to the column progression (i.e. left/right) fail. Need a tweak.

# ( 2,-1,-1)   0505 (-1,-1)    ok
# (-1,-1, 2)   0508 (-1, 2)    ok
# ( 1, 1,-2)   0705 ( 1,-1)    ok
# (-2, 1, 1)   0708 ( 1, 2)    ok
# (-1, 2,-1)   0806 ( 2, 0)    not ok, algorithm produces ( 2, 1)
# (-2, 4,-2)   1006 ( 4, 0)    not ok, algorithm produces ( 4, 2)
# (-1, 5,-4)   1105 ( 5,-1)    not ok, algorithm produces ( 5, 1)
# (-4, 5,-1)   1108 ( 5, 2)    not ok, algorithm produces ( 5, 4)
# ( 1,-2, 1)   0406 (-2, 0)    not ok, algorithm produces (-2, 1)
# ( 2,-4, 2)   0206 (-4, 0)    not ok, algorithm produces (-4, 2)
#
# so, looking at the sectors, the signs for the first and third
# coordinate may reveal which is which:
#
# left      (+,,+)   col < 0
# right     (-,,-)   col > 0
# top-left  (+,,-)   col < 0
# top-right (+,,-)   col > 0
# bot-left  (-,,+)   col < 0
# bot-right (-,,+)   col > 0
#
# axial rows have one value at 0, so may belong to two sectors,
# need to validate - but if so, current simple implementation
# should work (does in cases tried thus far...)
#
# referencing my older project, I only converted from traveller
# coords to three-axis (and not the reverse) so I could use
# it internally for distance calculations. The formulae were:
#
# x = column - 1
# y = -x - z
# z = (row - 1) - floor((column - 1)/2)
#
# This was only vetted for a single subsector, so just one
# quadrant of an inverted cartesian grid. And I didn't bother
# translating away from origin, so IIRC it works from 0101.
# Also, look like I used the first coordinate as column, instead
# of second. But it's something to work with...
#
# To match this implementation, need to change x/y/z up, and
# also remove -1 offset.
#
# x = row - floor(column/2)
# y = column
# z = -x - y


# World generation from Traveller '77 Book 3 pp. 4-12
# constraints based on the tables, though the dice throws
# in the text can produce values outside this range in
# some cases
class StarSystemFactory:
    """Builds StarSystem objects using the Traveller '77 rules."""

    # pylint: disable=R0913
    # R0913: Too many arguments (12/5)
    @classmethod
    def create(cls, name: str, coordinate: Coordinate, starport: str,
               size: int, atmosphere: int, hydrographics: int, population: int,
               government: int, law: int, tech: int, gas_giant: bool = True) -> StarSystem:
        """Create an instance of a StarSystem with pre-determined statistics."""
        uwp = UWP(starport, size, atmosphere, hydrographics,
                  population, government, law, tech)
        return StarSystem(name, coordinate, uwp, gas_giant)

    @classmethod
    def generate(cls, coordinate: Coordinate) -> StarSystem:
        """Randomly generate a StarSystem instance."""
        name = get_world_name()

        starport = StarSystemFactory._generate_starport()
        size = StarSystemFactory._generate_size()
        atmosphere = StarSystemFactory._generate_atmosphere(size)
        hydrographics = StarSystemFactory._generate_hydrographics(size, atmosphere)
        population = StarSystemFactory._generate_population()
        government = StarSystemFactory._generate_government(population)
        law = StarSystemFactory._generate_law(government)
        tech = StarSystemFactory._generate_tech(starport, size, atmosphere,
                                                hydrographics, population, government)

        gas_giant = bool(die_roll(2) < 10)

        uwp = UWP(starport, size, atmosphere, hydrographics,
                  population, government, law, tech)

        return StarSystem(name, coordinate, uwp, gas_giant)

    @classmethod
    def _generate_starport(cls) -> str:
        """Generate the starport classification for the UWP."""
        roll = die_roll(2)
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
        return starport

    @classmethod
    def _generate_size(cls) -> int:
        """Generate size value for the UWP."""
        die_modifier = -2
        return die_roll(2) + die_modifier

    @classmethod
    def _generate_atmosphere(cls, size: int) -> int:
        """Generate atmosphere value for the UWP."""
        if size == 0:
            return 0

        die_modifier = size - 7
        return constrain(die_roll(2) + die_modifier, 0, 12)

    @classmethod
    def _generate_hydrographics(cls, size: int, atmosphere: int) -> int:
        """Generate hydrographics value for the UWP."""
        if size <= 1:
            return 0

        die_modifier = size - 7
        if atmosphere <= 1 or atmosphere > 9:
            die_modifier -= 4
        return constrain(die_roll(2) + die_modifier, 0, 10)

    @classmethod
    def _generate_population(cls) -> int:
        """Generate population value for the UWP."""
        die_modifier = -2
        return die_roll(2) + die_modifier

    @classmethod
    def _generate_government(cls, population: int) -> int:
        """Generate government value for the UWP."""
        die_modifier = population - 7
        return constrain(die_roll(2) + die_modifier, 0, 13)

    @classmethod
    def _generate_law(cls, government: int) -> int:
        """Generate law value for the UWP."""
        die_modifier = government - 7
        return constrain(die_roll(2) + die_modifier, 0, 9)

    @classmethod
    def _generate_tech(cls, starport: str, size: int, atmosphere: int,
                       hydrographics: int, population: int, government: int) -> int:
        """Generate tech value for the UWP."""
        die_modifier = StarSystemFactory._starport_tech_modifier(starport)
        die_modifier += StarSystemFactory._size_tech_modifier(size)
        die_modifier += StarSystemFactory._atmosphere_tech_modifier(atmosphere)
        die_modifier += StarSystemFactory._hydrographics_tech_modifier(hydrographics)
        die_modifier += StarSystemFactory._population_tech_modifier(population)
        die_modifier += StarSystemFactory._government_tech_modifier(government)

        return constrain(die_roll() + die_modifier, 0, 18)

    @classmethod
    def _starport_tech_modifier(cls, starport: str) -> int:
        """Calculate the tech level modifier from starport."""
        if starport == "A":
            return 6
        if starport == "B":
            return 4
        if starport == "C":
            return 2
        if starport == "X":
            return -2
        return 0

    @classmethod
    def _size_tech_modifier(cls, size: int) -> int:
        """Calculate the tech level modifier from size."""
        if size in (0, 1):
            return 2
        if size in (2, 3, 4):
            return 1
        return 0

    @classmethod
    def _atmosphere_tech_modifier(cls, atmosphere: int) -> int:
        """Calculate the tech level modifier from atmosphere."""
        if atmosphere in (0, 1, 2, 3, 10, 11, 12):
            return 1
        return 0

    @classmethod
    def _hydrographics_tech_modifier(cls, hydrographics: int) -> int:
        """Calculate the tech level modifier from hydrographics."""
        if hydrographics == 9:
            return 1
        if hydrographics == 10:
            return 2
        return 0

    @classmethod
    def _population_tech_modifier(cls, population: int) -> int:
        """Calculate the tech level modifier from population."""
        if population in (1, 2, 3, 4, 5):
            return 1
        if population == 9:
            return 2
        if population == 10:
            return 4
        return 0

    @classmethod
    def _government_tech_modifier(cls, government: int) -> int:
        """Calculate the tech level modifier from government."""
        if government in (0, 5):
            return 1
        if government == 13:
            return -2
        return 0


class StarMap:
    """Represents a map of StarSystems laid out on a hexagonal grid."""

    def __init__(self, systems: Dict[Coordinate, Hex]) -> None:
        """Create an instance of a StarMap."""
        self.systems = systems
        for key in self.systems.keys():
            if not StarMap._valid_coordinate(key):
                raise ValueError(f"Invalid three-axis coordinate: {key}")

    def get_systems_within_range(self, origin: Coordinate, distance: int) -> List[StarSystem]:
        """Return a list of all StarSystems within the specified range in hexes."""
        result = []
        for coord in StarMap._get_coordinates_within_range(origin, distance):
            if coord in self.systems:
                if isinstance(self.systems[coord], StarSystem):
                    result.append(self.systems[coord])
            else:
                system = StarMap._generate_new_system(coord)
                self.systems[coord] = system
                if isinstance(system, StarSystem):
                    result.append(system)

        # although we only add StarSystems to the list,
        # mypy doesn't recognize that and we need to cast
        return cast(List[StarSystem], result)

    def get_system_at_coordinate(self, coordinate: Coordinate) -> Hex:
        """Return the contents of the specified coordinate, or create it."""
        return self.systems.get(coordinate, StarMap._generate_new_system(coordinate))

    def get_all_systems(self) -> List[StarSystem]:
        """Return all known StarSystems contained in the StarMap."""
        systems = [s for i,(k,s) in enumerate(self.systems.items()) if
                   isinstance(s, StarSystem)]
        systems = sorted(systems, key=lambda system: system.coordinate)
        return systems

    @classmethod
    def _generate_new_system(cls, coordinate: Coordinate) -> Hex:
        """Randomly create either a StarSystem or a DeepSpace instance."""
        if randint(1,6) >= 4:
            return StarSystemFactory.generate(coordinate)
        return DeepSpace(coordinate)

    @classmethod
    def _distance_between(cls, first: Coordinate, second: Coordinate) -> int:
        """Calculate the distance between two three-axis coordinates."""
        transformed = (second[0]-first[0],
                       second[1]-first[1],
                       second[2]-first[2])
        return max(abs(transformed[0]),
                   abs(transformed[1]),
                   abs(transformed[2]))

    @classmethod
    def _valid_coordinate(cls, coord: Coordinate) -> bool:
        """Test whether a given tuple is a valid three-axis coordinate."""
        return sum(coord) == 0

    # TO_DO: should we default origin param to (0,0,0)?
    @classmethod
    def _get_coordinates_within_range(cls, origin: Coordinate,
                                      radius: int) -> List[Coordinate]:
        """Return a list of all three-axis coordinate within a given range of an origin."""
        full_list = StarMap._get_all_coords(radius)

        filtered = [a for a in full_list if sum(a)==0]
        filtered.remove((0,0,0))

        translated = [(f[0] + origin[0],
                       f[1] + origin[1],
                       f[2] + origin[2]) for f in filtered]

        return translated

    @classmethod
    def _get_all_coords(cls, radius: int) -> List[Coordinate]:
        """Return a list of tuples, including both valid and invalid coordinates."""
        span = range(-radius, radius+1)
        return [(a,b,c) for a in span
                        for b in span
                        for c in span]

    @classmethod
    def convert_3_axis(cls, coord: Coordinate, origin: Tuple[int, int]) -> Tuple[int, int]:
        """Convert a three-axis coordinate to Traveller grid coordinates."""
        if coord[1] > 0:
            return (origin[0]+coord[1], origin[1]-coord[0])
        return (origin[0]+coord[1], origin[1]+coord[2])
