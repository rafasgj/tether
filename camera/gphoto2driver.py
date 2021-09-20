"""Driver for libgphoto2."""

import io
import gphoto2 as gp  # pylint: disable=import-error


class GPhoto2Error(Exception):
    """Raised when camera object is not ready for use."""

    def __init__(self, msg=None):
        """Initialize exception object."""
        super().__init__(
            "Camera object not initialized%s"
            % ((": %s" % msg) if msg else ".")
        )


class GPhoto2Driver:
    """Abstract the usage for GPhoto2 with higher level commands."""

    @staticmethod
    def autodetect():
        """Return a list of camera/port pairs."""
        _, cameras = gp.gp_camera_autodetect()
        return tuple(tuple(camport) for camport in cameras)

    def __init__(self, port=None):
        self.__config = None
        self.__port = port
        self.__cam = None
        self.__ctx = None
        self.__init_cam(port)

    def __init_cam(self, port):
        try:
            self.__ctx = gp.Context()
            self.__cam = gp.Camera()
            if port is not None:
                port_info_list = gp.PortInfoList()
                port_info_list.load()
                idx = port_info_list.lookup_path(port)
                self.__cam.set_port_info(port_info_list[idx])
            self.__cam.init(self.__ctx)
        except gp.GPhoto2Error as gpex:
            self.__invalidate_cam()
            if gpex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                error = "No camera found."
            else:
                error = str(gpex)
            msg = "{} GPhoto2 Error Code: {}"
            raise GPhoto2Error(msg.format(error, gpex.code)) from None
        else:
            self.__config = self.__cam.get_config()

    def __invalidate_cam(self):
        if self.is_ready:
            self.__cam.exit(self.__ctx)
            self.__cam = None
            self.__ctx = None

    def __del__(self):
        """Clean up camera resources."""
        self.__invalidate_cam()

    @property
    def is_ready(self):
        return self.__cam is not None

    def get_choices_for(self, name):
        """Return a list of elements for a CameraSettingCombo."""
        widget = self.__get_widget(name)
        return None if widget is None else list(widget.get_choices())

    def restart(self):
        self.__invalidate_cam()
        self.__init_cam(self.__port)

    def __get_widget(self, name):
        try:
            return self.__config.get_child_by_name(name)
        except Exception:
            raise GPhoto2Error("Invalid widget '{}''".format(name)) from None

    def get_attribute(self, name):
        if not self.is_ready:
            raise GPhoto2Error("Device not ready.")
        try:
            widget = self.__get_widget(name)
            return widget.get_value()
        except:  # noqa # pylint: disable=W0702
            abilities = self.__cam.get_abilities()
            if hasattr(abilities, name):
                return getattr(abilities, name)
        raise GPhoto2Error("Invalid attribute '{}''".format(name))

    def set_attribute(self, name, value):
        widget = self.__get_widget(name)
        widget.set_value(value)
        self.__cam.set_config(self.__config)

    def can_capture_image(self):
        """Query if the camera can capture images."""
        if self.is_ready:
            abilities = self.__cam.get_abilities()
            flags = gp.GP_OPERATION_CAPTURE_IMAGE
            flags |= gp.GP_OPERATION_CAPTURE_PREVIEW
            return abilities.operations & flags
        return False

    def __capture_from_camera(self):
        fileinfo = self.__cam.capture(gp.GP_CAPTURE_IMAGE, self.__ctx)
        filename = fileinfo.name
        filepath = fileinfo.folder
        file = self.__cam.file_get(filepath, filename, gp.GP_FILE_TYPE_NORMAL)
        return fileinfo, file

    def capture_to_file(self, filename=None):
        """Capture an image."""
        info, file = self.__capture_from_camera()
        filename = str(filename or info.name)
        gp.gp_file_save(file, filename)
        return filename

    def capture_to_stream(self):
        _, file = self.__capture_from_camera()
        _, filedata = gp.gp_file_get_data_and_size(file)
        return io.BytesIO(filedata)

    def __getitem__(self, name):
        return self.get_attribute(name)

    def __setitem__(self, name, value):
        self.set_attribute(name, value)
