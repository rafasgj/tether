"""CameraDriver interface."""

from typing import Any


class CameraDriver:
    """Define the camera driver interface."""

    def get_choices_for(self, setting: str) -> list:
        """
        Retrieve list of options for a specific setting.

        Parameters
        ----------
        setting: string
            The setting name.

        Return
        ------
        List of options for the camera setting.

        """
        raise NotImplementedError()

    def get_value_for(self, setting: str) -> Any:
        """
        Retrieve the camera value for a specific setting.

        Parameters
        ----------
        setting: string
            The setting name.

        """
        raise NotImplementedError()
