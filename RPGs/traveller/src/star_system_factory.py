"""Contains functions to construct a StarSystem.

StarSystemFactory - builds StarSystem objects using the Traveller '77 rules.
"""
from src.coordinate import Coordinate
from src.star_system import StarSystem, UWP
from src.utilities import die_roll, constrain
from src.word_gen import get_world_name

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
