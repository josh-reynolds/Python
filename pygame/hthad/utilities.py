"""Contains utility functions."""
from typing import List, Callable, Tuple
from pvector import PVector
from constants import BEAD
from entity import Entity
from location import Location

def get_all_entities(locs: List[Location]) -> List[Entity]:
    """Return a list of all Entities on the map."""
    entities = []
    for location in locs:
        if isinstance(location, Location) and location.contents:
            entities.append(location.contents)
    return entities

def check_for_connections(room: Location, locs: List[Location]) -> None:
    """Test whether a newly-added room collides with an existing one, and link up if so."""
    cavities = [l for l in locs if isinstance(l, Location)]
    if room in cavities:
        cavities.remove(room)
    for location in cavities:
        if room.intersects(location):
            print(f"Intersection detected: {room} - {location}")
            room.add_neighbor(location)

def create_location(location_type: Callable, coordinate: PVector,
                    size: Tuple[int,int]=(BEAD,BEAD)) -> Location:
    """Create a new location and add to the list."""
    new_location = location_type(coordinate=coordinate, size=size)
    # TO_DO: commented out while check_for_connections is fixed up
    #check_for_connections(new_location)
    return new_location
