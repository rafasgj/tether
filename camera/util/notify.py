"""Notify mechanism."""

from collections.abc import Callable


class Notifiable:
    """Implement a basic signaling mechanism."""

    def __init__(self, /, connectors=None):
        """
        Initialize notification mechanism.

        Parameters
        ----------
            connectors: list of string
                The list of signals the object exposes.

        """
        if not (connectors and isinstance(connectors, (tuple, list))):
            raise ValueError(f"Invalid connectors list: {connectors}")
        self.__pins = {}
        for connector in connectors:
            self.__pins[connector] = set()

    def connect(self, connector: str, callable: Callable) -> None:
        """
        Register a callback to a notification connector.

        Parameters
        ----------
            connector: string
                The signal name to connect.
                Any of 'previous', 'next', 'change'.
            callable: Callable
                The callable that will be called upon signal notification.

        """
        if connector not in self.__pins:
            raise ValueError(f"Connector not found: {connector}")
        self.__pins[connector].add(callable)

    def _notify(self, connectors: list[str]) -> None:
        """
        Notify all receivers registered for the connectors.

        This function should be called by derived classes.

        Parameters
        ----------
            connectors: list of strings
                Connectors to be notified.

        """
        for connector in connectors:
            for callable in self.__pins[connector]:
                callable(self)
