"""Contains classes to represent locations on the map."""
from typing import Tuple, Self, List
from pygame import Rect
from engine import screen
from pvector import PVector

# TO_DO: should be ABS
class Location():
    """Base class for game map locations."""

    def __init__(self, coordinate: PVector, name: str, color: Tuple, size: int) -> None:
        """Create an instance of a Location object."""
        self.name = name
        self.color = color

        self._coordinate = coordinate
        self.size = size
        self.rect = Rect(self._coordinate.x - self.size/2,
                         self._coordinate.y - self.size/2,
                         self.size,
                         self.size)
        self.tunnels = []
        self.neighbors = []
        self.visited = False
        self.contents = None

    def __repr__(self) -> str:
        """Return the string representation of a Location object."""
        return self.name

    def __hash__(self) -> int:
        """Return the hash value of a Location object."""
        return hash((self.name, self._coordinate))

    @property
    def coordinate(self) -> PVector:
        """Return the Location's coordinates."""
        return self._coordinate

    @coordinate.setter
    def coordinate(self, coord: PVector) -> None:
        """Set the Location's coordinates (and rect, implicitly)."""
        self._coordinate = coord
        self.rect = Rect(self.coordinate.x - self.size/2,
                         self.coordinate.y - self.size/2,
                         self.size,
                         self.size)

    def add_neighbor(self, neighbor: Self, bidi: bool=True) -> None:
        """Add a neighbor to this location."""
        self.neighbors.append(neighbor)
        if bidi:
            neighbor.add_neighbor(self, False)

    # TO_DO: currently only works for Rooms, which are rects
    #        Caverns are circles, so we'll need to adjust
    def intersects(self, other: Self) -> bool:
        """Test if a Location intersects with another."""
        return self.rect.colliderect(other.rect)

    def draw_shape(self) -> None:
        """Draw the Location on the screen.

        Should be overridden by child classes."""

    def draw(self) -> None:
        """Draw the Location on the screen."""
        self.draw_shape()

        #if self.contents:
            #y_offset = -10
        #else:
            #y_offset = 0

        #if SHOW_LABELS:
            #screen.draw.text(self.name,
                             #center=(self.coordinate.x, self.coordinate.y + y_offset),
                             #color = (255,255,255))
#
        #if self.contents and SHOW_LABELS:
            #screen.draw.text(f"{self.contents}",
                             #center=(self.coordinate.x, self.coordinate.y - y_offset),
                             #color = (255,255,255))

        # TO_DO: we're drawing these twice, once from each direction...
        for n in self.neighbors:
            screen.draw.line(self.color,
                             (self.coordinate.x, self.coordinate.y),
                             (n.coordinate.x, n.coordinate.y),
                             12)
            # TO_DO: kludge to fix overdraw problem
            if n.contents:
                n.contents.draw()

        if self.contents:
            self.contents.draw()

    # TO_DO: generalize the BFS pattern
    def get_all_connected_locations(self) -> List:
        """Use BFS to gather all Locations connected to self."""
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)

            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True

        for location in visited:
            location.visited = False

        return visited

    def get_all_connected_tunnels(self) -> List:
        """Use BFS to gather all tunnels (connections) connected to self."""
        tunnels = [(self,b) for b in self.neighbors]
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)

            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    tunnels += [(neighbor,b) for b in neighbor.neighbors
                                if (b, neighbor) not in tunnels]
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True

        for location in visited:
            location.visited = False

        return tunnels

    def get_locations_by_name(self, location_name: str) -> List:
        """Use BFS to gather all Locations matching a given name connected to self."""
        locations = []
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)
            if current_location.name == location_name:
                locations.append(current_location)

            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True

        for location in visited:
            location.visited = False

        return locations

    def get_all_matching_entities(self, entity_name) -> List:
        """Use BFS to gather all Entities reachable from self."""
        entities = []
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)
            if current_location.contents and current_location.contents.name == entity_name:
                entities.append(current_location.contents)

            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True

        for location in visited:
            location.visited = False

        return entities

    def distance_to(self, goal) -> int:
        """Use BFS to calculate the graph distance (connections) from self to a target Location."""
        # need to consider case when location is not connected to self
        distances = { self : 0 }
        visited = [self]
        queue = [self]
        self.visited = True

        while queue:
            current_location = queue.pop(0)

            if current_location == goal:
                break

            for neighbor in current_location.neighbors:
                if not neighbor.visited:
                    distances[neighbor] = distances[current_location] + 1
                    visited.append(neighbor)
                    queue.append(neighbor)
                    neighbor.visited = True

        for location in visited:
            location.visited = False

        return distances[goal]     # I think we'll get a KeyError here if goal not in graph...


class Cavern(Location):
    """Represents a Cavern location."""

    def __init__(self, coordinate: PVector, color=(129,128,128), contents=None,
                 tunnel: bool=False, tilt: int=0, name: str="Cavern") -> None:
        """Create an instance of a Cavern object."""
        super().__init__(coordinate, name, color, 30)
        self.contents = contents

        self.radius = self.size//2
        self.tunnel = tunnel        # TO_DO: confusing with graph edge tunnels
        self.tilt = tilt

    def update(self) -> None:
        """Update the Cavern object once per frame."""

    def draw_shape(self) -> None:
        """Draw the Cavern object to the screen once per frame."""
        screen.draw.circle(self.coordinate.x, self.coordinate.y, self.radius, self.color, 0)

        if self.tunnel:
            screen.draw.line(self.color,
                             (self.coordinate.x - 85, self.coordinate.y - self.tilt),
                             (self.coordinate.x + 85, self.coordinate.y + self.tilt),
                             12)


class Room(Location):
    """Represents a Room location."""

    def __init__(self, coordinate: PVector, color=(128,128,128),
                 contents=None, name: str="Room") -> None:
        """Create an instance of a Room object."""
        super().__init__(coordinate, name, color, 30)
        self.contents = contents

    def update(self) -> None:
        """Update the Room object once per frame."""

    def draw_shape(self) -> None:
        """Draw the Room object to the screen once per frame."""
        screen.draw.rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h, self.color, 0)
