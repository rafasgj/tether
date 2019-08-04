"""Holds camera settings."""

import os
import os.path
import gphoto2 as gp
from util.formatter import FilenameFormatter
from util import OptionListModel


class Camera(object):
    """Abstract the usage for GPhoto2 with higher level commands."""

    # TODO: autopoweroff (TEXT)
    config_properties = ['focusmode', 'drivemode', 'imageformat',
                         'shutterspeed', 'aperture', 'iso', 'meteringmode',
                         'whitebalance']
    readonly_properties = ['shuttercounter', 'lensname', 'serialnumber',
                           'batterylevel']

    @staticmethod
    def autodetect():
        """Return a list of camera/port pairs."""
        count, cameras = gp.gp_camera_autodetect()
        return ([tuple(camport) for camport in cameras])

    def __init__(self, port=None, capture_directory=os.getcwd()):
        """Initialize the camera object."""
        self.last_error = None
        self.port = port
        self.capture_directory = capture_directory
        self.__frame_grab = None
        self.filename_formatter = FilenameFormatter()
        self.__init_cam()

    def set_filename_format(self, format):
        """Set the rule to name pictures taken."""
        self.filename_formatter.format = format

    def __create_setting_model(self, var):
        model = self.get_setting_model(var)
        value = getattr(self, var)
        return OptionListModel(model, value)

    def __init_cam(self):
        try:
            self.ctx = gp.Context()
            self.cam = gp.Camera()
            if self.port is not None:
                port_info_list = gp.PortInfoList()
                port_info_list.load()
                idx = port_info_list.lookup_path(self.port)
                self.cam.set_port_info(port_info_list[idx])
            self.cam.init(self.ctx)
            self.config = self.cam.get_config()
            self.iso_model = self.__create_setting_model("iso")
            self.shutterspeed_model = \
                self.__create_setting_model("shutterspeed")
            self.aperture_model = self.__create_setting_model("aperture")

        except gp.GPhoto2Error as gpex:
            if gpex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                error = "No camera found. Connect your camera and turn it on."
                self.last_error = error
            else:
                self.last_error = "GPhoto2 Error Code: {}".format(gpex.code)
            self.cam = None
            self.ctx = None
        except Exception as ex:
            self.cam = None
            self.ctx = None
            self.last_error = str(ex)
        return self.cam

    def on_frame_grab(self, callable):
        """Set callable to be called when a new picture is taken."""
        self.__frame_grab = callable

    @property
    def ready(self):
        """Query if a camera is ready."""
        return self.cam is not None

    def __restart(self):
        if self.cam is None:
            self.__init_cam()
            if self.cam is None:
                error = "Camera was not correctly initiated.\nLast Error: {}"
                raise Exception(error.format(self.last_error))

    def __get_widget(self, name):
        self.__restart()
        return self.config.get_child_by_name(name)

    def __get_config(self, name):
        self.__restart()
        return self.__get_widget(name).get_value()

    def __set_config(self, name, value):
        bk = self.__get_config(name)
        try:
            self.__get_widget(name).set_value(value)
            self.cam.set_config(self.config)
        except Exception as ex:
            error = "Invalid config value '{}' for '{}'."
            self.last_error = error.format(value, name)
            self.__set_config(name, bk)

    def set_capture_directory(self, path):
        """Set Capture Directory."""
        self.capture_directory = path

    @property
    def capture_directory(self):
        """Retrieve the directory images will be captured to."""
        return self.__capture_directory

    @capture_directory.setter
    def capture_directory(self, directory):
        """Set the directory images will be captured to."""
        self.__capture_directory = directory

    def __capture_to_file(self):
        """Capture an image."""
        self.__restart()
        img = self.cam.capture(gp.GP_CAPTURE_IMAGE, self.ctx)
        filename = img.name
        filepath = img.folder
        file = self.cam.file_get(filepath, filename, gp.GP_FILE_TYPE_NORMAL)
        filename = os.path.join(self.capture_directory,
                                self.filename_formatter.filename(filename))
        gp.gp_file_save(file, filename)
        return filename

    @property
    def model(self):
        """Retrieve camera model."""
        return self.cam.get_abilities().model

    def __setattr__(self, name, value):
        """Overide 'setters' to easily deal with camera properties."""
        if name in Camera.config_properties:
            self.__set_config(name, value)
        else:
            super().__setattr__(name, value)

    def __getattribute__(self, name):
        """Overide 'getters' to easily deal with camera properties."""
        if name in Camera.config_properties + Camera.readonly_properties:
            return self.__get_config(name)
        else:
            return super().__getattribute__(name)

    def __get_choices(self, name):
        widget = self.__get_widget(name)
        return [c for c in widget.get_choices()]

    def get_setting_model(self, name):
        """Return a list of elements for a CameraSettingCombo."""
        widget = self.__get_widget(name)
        return [c for c in widget.get_choices()]

    def reset_error(self):
        """Clear last error attribute."""
        self.last_error = None

    def __del__(self):
        """Clean up camera resources."""
        if self.cam is not None:
            self.cam.exit(self.ctx)

    def grab_frame(self, *args):
        """Grabe a frame from camera."""
        self.shutterspeed = self.shutterspeed_model.value
        self.aperture = self.aperture_model.value
        self.iso = self.iso_model.value
        filename = self.__capture_to_file()
        if self.__frame_grab is not None:
            self.__frame_grab(self, filename)
