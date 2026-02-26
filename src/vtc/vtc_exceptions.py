class NoQuotaError(Exception):
    """Raised when a locally maintained quota is exceeded."""
    pass

class VerificationError(Exception):
    """Raised when data verification fails."""
    pass


class EmptyQueueError(Exception):
    """Raised when the queue is empty."""
    pass