"""Contains utility functions."""
from typing import List, Callable, Tuple
from pvector import PVector
from intersections import rect_segment_intersects
from constants import BEAD, WIDTH, GROUND_LEVEL, HEIGHT
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

def create_location(location_type: Callable,
                    coordinate: PVector,
                    locs: List[Location],
                    size: Tuple[int,int]=(BEAD,BEAD)) -> Location:
    """Create a new location and add to the list."""
    new_location = location_type(coordinate=coordinate, size=size)
    check_for_connections(new_location, locs)
    return new_location

def in_bounds(point: PVector) -> bool:
    """Test whether the given point is within the underground region of the screen."""
    return 0 <= point.x <= WIDTH and GROUND_LEVEL <= point.y <= HEIGHT

def out_of_bounds(point: PVector) -> bool:
    """Test whether the given point is outside the underground region of the screen."""
    return not in_bounds(point)

def is_viable(candidate_room: Location, nodes: List[Location], edges: List[Tuple]) -> bool:
    """Test whether a candidate location is legal."""
    for location in nodes:
        if candidate_room.intersects(location):
            return False

    tunnel_coords = [(a.coordinate, b.coordinate) for a,b in edges]
    for tunnel in tunnel_coords:
        if rect_segment_intersects(candidate_room.rect, tunnel):
            return False

    if out_of_bounds(candidate_room.coordinate):
        return False

    return True
