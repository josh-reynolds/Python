"""Contains the StarMap class.

StarMap - represents a map of StarSystems laid out on a hexagonal grid.
"""
from random import randint
from typing import Dict, List, cast, Tuple
from src.coordinate import Coordinate
from src.star_system import StarSystem, DeepSpace, Hex
import src.star_system_factory
from src.subsector import Subsector
from src.word_gen import get_subsector_name

class StarMap:
    """Represents a map of StarSystems laid out on a hexagonal grid."""

    def __init__(self, systems: Dict[Coordinate, Hex]) -> None:
        """Create an instance of a StarMap."""
        self.systems = systems
        for key in self.systems.keys():
            if not key.is_valid():
                raise ValueError(f"Invalid three-axis coordinate: {key}")
        self.subsectors: Dict[Tuple[int,int], Subsector] = {
                (0,0) : Subsector("ORIGIN", (0,0)),
                }

    def __repr__(self) -> str:
        """Return the developer string representation of a StarMap object."""
        return f"StarMap({self.systems!r})"

    def list_map(self) -> List[str]:
        """Return a list of all Hexes in the map, as strings."""
        system_list = []
        for system in self.systems.items():
            system_list.append(f"{system[0].trav_coord[1]} : " +
                               f"{self.get_subsector_string(system[1])} : " + 
                               f"{system[1]}\n")
        system_list.sort()
        return system_list

    def get_subsector_string(self, system: Hex) -> str:
        """Return the subsector coordinates for a given StarSystem."""
        coord = system.coordinate.trav_coord
        return self.pretty_coordinates(coord)

    def pretty_coordinates(self, coord: Tuple[Tuple[int, int], Tuple[int, int]]) -> str:
        """Return the string representation of an absolute Traveller coordinate.

        Input coordinates are in the form ((x, y), (i, j)) where x / y are the hex
        coordinates within a subsector (ranging from (1,1) to (8,10)) and i / j are
        the coordinates of the subsector itself.
        """
        hex_coord, sub_coord = coord
        hex_string = str(hex_coord[0]).zfill(2) + str(hex_coord[1]).zfill(2)

        if sub_coord in self.subsectors:
            sub = self.subsectors[sub_coord]
        else:
            sub = _generate_new_subsector(sub_coord)
            self.subsectors[sub_coord] = sub
        sub_string = sub.name

        return f"{sub_string} {hex_string}"

    def get_systems_in_subsector(self, sub_coord: Tuple[int,int]) -> List[Coordinate]:
        """Return list of all StarSystems in the given Subsector."""
        return [c for c in self.systems if c.trav_coord[1] == sub_coord]

    def get_systems_within_range(self, origin: Coordinate, distance: int) -> List[StarSystem]:
        """Return a list of all StarSystems within the specified range in hexes."""
        result = []
        for coord in _get_coordinates_within_range(origin, distance):
            if coord in self.systems:
                if isinstance(self.systems[coord], StarSystem):
                    result.append(self.systems[coord])
            else:
                system = _generate_new_system(coord)
                self.systems[coord] = system
                if isinstance(system, StarSystem):
                    result.append(system)

        # although we only add StarSystems to the list,
        # mypy doesn't recognize that and we need to cast
        return cast(List[StarSystem], result)

    # TO_DO: shouldn't we just implement get_items dunder method for this?
    def get_system_at_coordinate(self, coordinate: Coordinate) -> Hex:
        """Return the contents of the specified coordinate, or create it."""
        return self.systems.get(coordinate, _generate_new_system(coordinate))

    def get_all_systems(self) -> List[StarSystem]:
        """Return all known StarSystems contained in the StarMap."""
        systems = [s for i,(k,s) in enumerate(self.systems.items()) if
                   isinstance(s, StarSystem)]
        systems = sorted(systems, key=lambda system: system.coordinate)
        return systems


def _generate_new_subsector(coordinate: Tuple[int, int]) -> Subsector:
    """Return a new subsector."""
    name = get_subsector_name()
    return Subsector(name, coordinate)

def _generate_new_system(coordinate: Coordinate) -> Hex:
    """Randomly create either a StarSystem or a DeepSpace instance."""
    if randint(1,6) >= 4:
        return src.star_system_factory.generate(coordinate)
    return DeepSpace(coordinate)

def _get_coordinates_within_range(origin: Coordinate, radius: int) -> List[Coordinate]:
    """Return a list of all three-axis coordinate within a given range of an origin."""
    full_list = _get_all_coords(radius)

    filtered = [a for a in full_list if a.is_valid()]
    filtered.remove(Coordinate(0,0,0))

    translated = [Coordinate(f[0] + origin[0],
                             f[1] + origin[1],
                             f[2] + origin[2]) for f in filtered]
    return translated

def _get_all_coords(radius: int) -> List[Coordinate]:
    """Return a list of tuples, including both valid and invalid coordinates."""
    span = range(-radius, radius+1)
    return [Coordinate(a,b,c) for a in span
                              for b in span
                              for c in span]
