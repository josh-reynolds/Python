"""Contains utility functions."""
from typing import List
from entity import Entity
from location import Location

def get_all_entities(locs: List[Location]) -> List[Entity]:
    """Return a list of all Entities on the map."""
    entities = []
    for location in locs:
        if isinstance(location, Location) and location.contents:
            entities.append(location.contents)
    return entities

