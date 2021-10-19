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

"""Driver for libgphoto2."""

import io
import gphoto2  # pylint: disable=import-error

from photosuite.camera.cameradriver import CameraDriver


class GPhoto2Error(Exception):
    """Raised when camera object is not ready for use."""

    def __init__(self, msg=None):
        """Initialize exception object."""
        super().__init__(f"{msg}" if msg else "Unknown GPhoto2 error.")


class GPhoto2Driver(CameraDriver):
    """Abstract the usage for GPhoto2 with higher level commands."""

    @staticmethod
    def autodetect():
        """Return a list of camera/port pairs."""
        _, cameras = gphoto2.gp_camera_autodetect()
        return tuple(tuple(camport) for camport in cameras)

    def __init__(self, port=None):
        """
        Initialize camera object.

        Parameters
        ----------
        port: string (optional)
            Optionaly provide the camera port to use.

        """
        self.__port = port
        self.__config = None
        self.__cam = None
        self.__ctx = None
        self.__init_cam()

    def __init_cam(self):
        """Initialize the camera."""
        try:
            self.__ctx = gphoto2.Context()
            self.__cam = gphoto2.Camera()
            if self.__port is not None:
                port_info_list = gphoto2.PortInfoList()
                port_info_list.load()
                idx = port_info_list.lookup_path(self.__port)
                self.__cam.set_port_info(port_info_list[idx])
            self.__cam.init(self.__ctx)
        except gphoto2.GPhoto2Error as gpex:
            self.__invalidate_cam()
            if gpex.code == gphoto2.GP_ERROR_MODEL_NOT_FOUND:
                error = "No camera found."
            else:
                error = str(gpex)
            raise GPhoto2Error(f"{error} (error code: {gpex.code})") from None
        else:
            self.__config = self.__cam.get_config()

    def __invalidate_cam(self):
        """Close camera connection and cleanup object."""
        if self.is_ready:
            self.__cam.exit(self.__ctx)
            self.__cam = None
            self.__ctx = None

    def __del__(self):
        """Clean up camera resources."""
        self.__invalidate_cam()

    @property
    def is_ready(self):
        """Query if object (not the camera) is ready to use."""
        return self.__cam is not None

    def get_choices_for(self, setting):
        """Return a list of choices for a given setting."""
        widget = self.__get_widget(setting)
        return None if widget is None else list(widget.get_choices())

    def restart(self):
        """Restart camera connection."""
        self.__invalidate_cam()
        self.__init_cam()

    def __get_widget(self, name):
        """Retrieve a camera widget by name."""
        try:
            return self.__config.get_child_by_name(name)
        except Exception:
            raise GPhoto2Error(f"Invalid widget '{name}'") from None

    def get_value_for(self, setting):
        """Retrieve the current value of a camera setting."""
        if not self.is_ready:
            raise GPhoto2Error("Device not ready.")
        try:
            widget = self.__get_widget(setting)
            return widget.get_value()
        except:  # noqa # pylint: disable=W0702
            abilities = self.__cam.get_abilities()
            if hasattr(abilities, setting):
                return getattr(abilities, setting)
        raise TypeError(setting)

    def set_value_for(self, name, value):
        """Set the value of a camera setting."""
        widget = self.__get_widget(name)
        widget.set_value(value)
        self.__cam.set_config(self.__config)

    def can_capture_image(self):
        """Query if the camera can capture images."""
        if self.is_ready:
            abilities = self.__cam.get_abilities()
            flags = (
                gphoto2.GP_OPERATION_CAPTURE_IMAGE
                | gphoto2.GP_OPERATION_CAPTURE_PREVIEW
            )
            return abilities.operations & flags
        return False

    def __capture_from_camera(self):
        """Capture image from camera."""
        fileinfo = self.__cam.capture(gphoto2.GP_CAPTURE_IMAGE, self.__ctx)
        filename = fileinfo.name
        filepath = fileinfo.folder
        file = self.__cam.file_get(
            filepath, filename, gphoto2.GP_FILE_TYPE_NORMAL
        )
        return fileinfo, file

    def capture_to_file(self, filename=None):
        """Capture an image to a file."""
        info, file = self.__capture_from_camera()
        filename = str(filename or info.name)
        gphoto2.gp_file_save(file, filename)
        return filename

    def capture_to_stream(self):
        """Capture an image to a BytesIO stream."""
        _, file = self.__capture_from_camera()
        _, filedata = gphoto2.gp_file_get_data_and_size(file)
        return io.BytesIO(filedata)

    def __getitem__(self, name):
        """Allow retrieval of camera settings as object properties."""
        return self.get_value_for(name)

    def __setitem__(self, name, value):
        """Allow setting of camera settings as object properties."""
        self.set_value_for(name, value)
