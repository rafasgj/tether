"""Define the UI to control camera settings."""

from gi.repository import Gtk
from .camerasettingbox import CameraSettingBox, CameraSettingCombo


class CameraControlBox(Gtk.Box):
    """Create box to control camera settings."""

    def __init__(self, camera, cb=None):
        """Initialize the UI composed component."""
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL,
                         spacing=10)
        self.set_homogeneous(False)
        self.camera = camera
        # Shutter Button
        self.pack_start(Gtk.Label(), True, True, 0)
        self.pack_start(self.__create_combo_settings(), False, False, 0)
        self.pack_end(Gtk.Label(), True, True, 0)
        self.pack_end(self.__create_shutter_button(), False, False, 0)
        # Camera Settings box
        internal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        internal.set_homogeneous(False)
        self.pack_start(internal, False, False, 0)
        settings = self.__create_camera_settings_box(camera)
        internal.pack_start(settings, False, False, 0)
        # Camera Properties box
        internal.pack_start(self.__create_camera_properties_box(camera.model,
                            camera.lensname), False, False, 0)

    def __create_shutter_button(self):
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        button_box.set_homogeneous(False)
        img = Gtk.Image()
        img.set_from_icon_name("camera-photo", Gtk.IconSize.DIALOG)
        label = Gtk.Label()
        label.set_markup("<big><b>SHOT!</b></big>")
        button_box.pack_start(img, False, False, 0)
        button_box.pack_end(label, False, False, 0)
        self.shutter_button = Gtk.Button()
        self.shutter_button.set_always_show_image(True)
        self.shutter_button.add(button_box)
        return self.shutter_button

    def __create_camera_settings_box(self, camera):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_homogeneous(False)
        shutter = CameraSettingBox("Shutter", camera.shutterspeed_model)
        aperture = CameraSettingBox("Aperture", camera.aperture_model)
        iso = CameraSettingBox("ISO", camera.iso_model)
        box.pack_start(shutter, False, False, 0)
        box.pack_start(aperture, False, False, 0)
        box.pack_start(iso, False, False, 0)
        return box

    def __create_combo_settings(self):
        """Create UI for Wite Balance and Image Format."""
        def set_value_if(model, _, iter, name):
            value = getattr(self.camera, name)
            if model[iter][0] == value:
                getattr(self, name).set_active_iter(iter)
                return True
            else:
                return False

        def create_combo(label, name):
            vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
            # TODO: this 3-line hack computes the alleged max label size.
            text = Gtk.Label(label=label)
            sz = Gtk.Label(label="WWWWWWW")
            sz.show()
            sz = sz.size_request()
            text.set_size_request(sz.width, sz.height)
            vbox.pack_start(text, False, False, 0)
            model = self.camera.get_setting_model(name)
            cb = CameraSettingCombo(model)
            setattr(self, name, cb)
            cb.get_model().foreach(set_value_if, name)
            cb.connect('changed',
                       lambda combo: setattr(self.camera, name, combo.value))
            vbox.pack_start(cb, True, True, 0)
            return vbox

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.pack_start(create_combo("White\nBalance", "whitebalance"),
                       False, False, 0)
        box.pack_start(create_combo("Image\nFormat", "imageformat",),
                       False, False, 0)
        return box

    def __create_camera_properties_box(self, model, lens):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_homogeneous(True)
        camera_model = Gtk.Label(label=model)
        lens_model = Gtk.Label(label=lens)
        box.pack_start(camera_model, False, False, 0)
        box.pack_start(lens_model, False, False, 0)
        return box

    def set_shutter_function(self, function):
        """Change the function called when activating camera shutter."""
        self.shutter_button.connect("clicked", function)
