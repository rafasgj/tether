"""Errors used by Camera abstraction."""


class CameraError(Exception):
    """Raised when an error occured while processing a camera task."""

    def __init__(self, msg=None):
        """Initialize exception object."""
        super().__init__("Camera error: %s" % (msg if msg else "Unkown"))
