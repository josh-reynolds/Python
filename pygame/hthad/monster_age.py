"""Contains the MonsterAge class and supporting functions."""
from typing import List

# Age of Monsters
# TO_DO: we'll need the Great Disaster too, not sure yet if that folds in here
#        or should be handled as its own 'Age'
class MonsterAge():
    """Manages creation of the landscape and entities during the Age of Monsters."""

    def __init__(self) -> None:
        """Create an instance of a MonsterAge object."""
        self.done = False
        self.name = "Age of Monsters"
        self.step = 0

    def update(self) -> List:
        """Return the next generated map location."""
        print("MonsterAge.update()")
        match self.step:
            case 0:
                # remove all dwarves and regular treasures
                all_entities = get_all_entities()
                for entity in all_entities:
                    match entity.name:
                        case "Dwarves" | "Treasure":
                            entity.parent.contents = None

                self.step += 1

            case 1:
                pass
        return []

    def is_done(self) -> bool:
        """Return whether the MonsterAge has completed or not."""
        return self.done
