"""Contains the HighportScreen class.

HighportScreen - contains commands for the highport state.
"""
from typing import Any
from src.model import Model
from src.play import PlayScreen

class HighportScreen(PlayScreen):
    """Contains commands for the highport state."""

    def __init__(self, parent: Any, model: Model) -> None:
        """Create a HighportScreen object."""
        super().__init__(parent, model)
        self.commands += [
                ]
        self.commands = sorted(self.commands, key=lambda command: command.key)

    def __repr__(self) -> str:
        """Return the developer string representation of the current screen."""
        return f"Highport({self.parent!r})"

    # VIEW COMMANDS ========================================================
    # STATE TRANSITIONS ====================================================
    # ACTIONS ==============================================================
