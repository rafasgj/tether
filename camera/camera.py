"""Holds camera settings."""

# import os
# import os.path
from util.formatter import FilenameFormatter
from util import OptionListModel

# try:
#     from PIL import Image
#     __NO_PIL_IMAGE__ = True
# except ImportError:
#     __NO_PIL_IMAGE__ = False

from camera.errors import CameraError
from camera.gphoto2driver import GPhoto2Driver, GPhoto2Error


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
            'model',
            'serialnumber',
            'batterylevel'
        ]
    }

    def __init__(self, port=None):
        """Initialize the camera object.

        Parameters:
            port: The libgphoto2 camera port for the camera.
        """
        self.__cam = GPhoto2Driver(port)
        self.filename_formatter = FilenameFormatter()
        self.models = dict(
            iso=self.__create_setting_model("iso"),
            shutter=self.__create_setting_model("shutterspeed"),
            aperture=self.__create_setting_model("aperture"),
        )

    def __create_setting_model(self, var):
        model = self.__cam.get_choices_for(var)
        if model is not None:
            return OptionListModel(model, getattr(self, var))
        return None

    def __getattr__(self, name):
        """Overide 'getters' to easily deal with camera properties."""
        props = Camera.properties['config'] + Camera.properties['readonly']
        if name in props:
            try:
                return self.__cam.get_attribute(name)
            except GPhoto2Error:
                return None
        return getattr(super(), name)

    def grab_frame(self, filename=None, **kwargs):
        """Grabe a frame from camera, to a file, or as a BytesIO stream.

        Parameters:
            filename: If set, grab image to this file.
        """
        if not self.__cam.can_capture_image():
            raise CameraError("Camera cannot capture images with GPhoto2.")
        for setting in ["shutterspeed", "aperture", "iso"]:
            value = kwargs.get(setting)
            if value:
                self.__cam[setting] = value
        if filename:
            filename = self.__cam.capture_to_file(filename)
            return filename
        return self.__cam.capture_to_stream()
