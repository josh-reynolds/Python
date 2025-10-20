"""Contains classes to manage game commands."""
from typing import Callable

# pylint: disable=R0903
# R0903: Too few public methods (0/2)
class Command:
    """Represents a command available to the player."""

    def __init__(self, key: str, description: str, action: Callable) -> None:
        """Create an instance of a Command."""
        self.key = key
        self.description = description
        self.action = action
