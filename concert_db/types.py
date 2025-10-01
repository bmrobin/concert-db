from typing import Protocol

from textual.notifications import SeverityLevel


class Notification(Protocol):
    """
    A type for a notification callback function.
    """

    def __call__(self, message: str, *, severity: SeverityLevel) -> None: ...
