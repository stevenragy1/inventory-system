"""Domain errors raised by the service layer.

The API layer maps these to HTTP responses; the UI only displays them.
"""


class DomainError(Exception):
    """Base class for business-rule violations."""

    status_code = 400


class NotFoundError(DomainError):
    status_code = 404


class DuplicateError(DomainError):
    status_code = 409


class OverIssueWarning(DomainError):
    """Stock-out would take the level below zero.

    Not written to the database. The caller must resubmit with confirm=True
    to record the movement with over_issue=True.
    """

    status_code = 409

    def __init__(self, available, requested):
        super().__init__(
            f"Only {available} available, requested {requested}."
        )
        self.available = available
        self.requested = requested

    def to_dict(self):
        return {
            "warning": True,
            "available": self.available,
            "requested": self.requested,
            "message": str(self),
        }
