"""Holds camera settings."""

from typing import Any

from util.formatter import FilenameFormatter
from util import OptionListModel

from camera.errors import CameraError

from camera.cameradriver import CameraDriver


class Camera:
    """Provides an abstraction to manage camera settings and capture images."""

    properties = {
        "config": [
            'focusmode',
            'drivemode',
            'imageformat',
            'meteringmode',
            'shutterspeed',
            'aperture',
            'iso',
            'whitebalance'
        ],
        "readonly": [
            'shuttercounter',
            'lensname',
            'cameramodel',
            'serialnumber',
            'batterylevel'
        ]
    }

    def __init__(self, camera_driver: CameraDriver) -> None:
        """Initialize the camera object.

        Parameters
        ----------
        cameradriver: The camera driver to use.
        """
        self.__cam = camera_driver
        self.filename_formatter = FilenameFormatter()
        self.models = dict(
            iso=self.__create_setting_model("iso"),
            shutterspeed=self.__create_setting_model("shutterspeed"),
            aperture=self.__create_setting_model("aperture"),
        )

    def __create_setting_model(self, setting: str) -> OptionListModel:
        model = self.__cam.get_choices_for(setting)
        if model is not None:
            return OptionListModel(model, getattr(self, setting))
        return None

    def __getattr__(self, name: str) -> Any:
        """Overide 'getters' to easily deal with camera properties."""
        props = Camera.properties['config'] + Camera.properties['readonly']
        if name in props:
            try:
                value = self.__cam.get_value_for(name)
                return value
            except TypeError:
                return None
        return getattr(super(), name)

    def grab_frame(self, filename=None, **kwargs):
        """Grab a frame from camera, to a file, or as a BytesIO stream.

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
