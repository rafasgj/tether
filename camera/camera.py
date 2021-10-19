# tether: GTK+ interface to control cameras using libgphoto2.
# Copyright (C) 2019  Rafael Guterres Jeffman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Holds camera settings."""

from typing import Any

from util.formatter import FilenameFormatter
from camera.util.optionlistmodel import OptionListModel

from camera.errors import CameraError

from camera.cameradriver import CameraDriver


class Camera:
    """Provides an abstraction to manage camera settings and capture images."""

    properties = {
        "config": [
            "focusmode",
            "drivemode",
            "imageformat",
            "meteringmode",
            "shutterspeed",
            "aperture",
            "iso",
            "whitebalance",
        ],
        "readonly": [
            "shuttercounter",
            "lensname",
            "cameramodel",
            "serialnumber",
            "batterylevel",
        ],
    }

    def __init__(self, camera_driver: CameraDriver, **options):
        """
        Initialize the camera object.

        Parameters
        ----------
        camera_driver: CameraDriver
            The camera driver to use.
        options: variable
            A list of optional configuration options;
            - set_on_capture: bool
                Control if settings take effect on capture (True) or
                imediatelly after model changes (False).
                Default to True

        """
        self.__cam = camera_driver
        self.filename_formatter = FilenameFormatter()
        set_on_capture = options.get("set_on_capture", True)
        self.models = {
            setting: self.__create_setting_model(setting, set_on_capture)
            for setting in ["iso", "shutterspeed", "aperture"]
        }

    def __create_setting_model(self, setting, set_on_capture=True):
        """Create an OptionListModel for camera setting."""
        result = None
        model = self.__cam.get_choices_for(setting)
        if model is not None:
            result = OptionListModel(model, getattr(self, setting))
            if not set_on_capture:
                result.connect("changed", self._on_setting_change)
        return result

    def _on_setting_change(self, _sender: OptionListModel) -> None:
        """Respond to setting change."""
        for setting, model in self.models.items():
            setattr(self, setting, model.value)

    def __getattr__(self, name: str) -> Any:
        """Overide 'getters' to easily deal with camera properties."""
        props = Camera.properties["config"] + Camera.properties["readonly"]
        if name in props:
            try:
                value = self.__cam.get_value_for(name)
                return value
            except TypeError:
                return None
        return getattr(super(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Overide 'getters' to easily deal with camera properties."""
        props = Camera.properties["config"] + Camera.properties["readonly"]
        if name in props:
            self.__cam.set_value_for(name, value)
        return super().__setattr__(name, value)

    def grab_frame(self, filename=None, **kwargs):
        """
        Grab a frame from camera, to a file, or as a BytesIO stream.

        Parameters
        ----------
        filename: string
            If set, grab image to this file.
        shutterspeed: string
            Camera shutter speed to use.
        aperture:
            Camera aperture to use.
        iso:
            Camera ISO (light sensitivity) value to use.

        Return
        ------
            The filename or the data stream.

        """
        if not self.__cam.can_capture_image():
            raise CameraError("Camera cannot capture images with GPhoto2.")
        for setting in ["shutterspeed", "aperture", "iso"]:
            model = self.models.get(setting)
            value = kwargs.get(setting, model.value if model else None)
            if value:
                self.__cam[setting] = value
        if filename:
            filename = self.__cam.capture_to_file(filename)
            return filename
        return self.__cam.capture_to_stream()
