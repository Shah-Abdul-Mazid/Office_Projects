class StorytellingServiceError(Exception):
    """Base exception for service layer failures."""


class ExternalServiceTimeoutError(StorytellingServiceError):
    """Raised when an external provider exceeds the configured timeout."""
