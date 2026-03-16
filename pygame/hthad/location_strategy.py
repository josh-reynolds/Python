"""Contains Strategy classes to build Locations and groups of Locations."""
from typing import Any, List
from location import Location

# TO_DO: should be an ABC
class LocationStrategy:
    """Base class for LocationStrategy builders."""

    def __init__(self) -> None:
        """Create an instance of a LocationStrategy object."""
        self.done = False

    def next(self, locs: List[Location]) -> Any | None:
        """Return the next location in the sequence."""
        self.done = True    # TO_DO: temporary to make stubs work
        return None

    def is_done(self) -> bool:
        """Return whether the LocationStrategy is complete or not."""
        return self.done


