"""Contains classes to create and manage a Traveller star map.

StarSystemFactory - builds StarSystem objects using the Traveller '77 rules.
StarMap - represents a map of StarSystems laid out on a hexagonal grid.
"""
from random import randint
from typing import Dict, List, cast
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
