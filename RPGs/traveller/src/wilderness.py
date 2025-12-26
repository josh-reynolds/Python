"""Contains the WildernessScreen class.

WildernessScreen - contains commands for the wilderness state.
"""
from typing import Any
from src.model import Model
from src.play import PlayScreen

class WildernessScreen(PlayScreen):
    """Contains commands for the wilderness state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a WildernessScreen object."""
        super().__init__(parent, model)
        self.commands += [
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Wilderness({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================
