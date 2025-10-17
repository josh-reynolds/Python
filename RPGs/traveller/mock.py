"""Contains mock classes for testing."""

# pylint: disable=R0903
# R0903: Too few public methods (1/2)
class ObserverMock:
    """Mocks an observer for testing."""

    def __init__(self) -> None:
        """Create an instance of an ObserverMock."""
        self.message = ""
        self.priority = ""

    def on_notify(self, message: str, priority: str) -> None:
        """Save message and priority for review on notification."""
        self.message = message
        self.priority = priority
