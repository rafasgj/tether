"""Define the UI to control camera settings."""

from gi.repository import Gtk
from .optionselector import OptionSelector
from .listcombobox import ListComboBox
from .functions import label_with_character_size


class CameraControlBox(Gtk.Box):
    """Create box to control camera settings."""

    def __init__(self, camera, cb=None):
        """Initialize the UI composed component."""
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL,
                         spacing=10)
        self.set_homogeneous(False)
        self.camera = camera
        # Combo settings
        cbs = [("White\nBalance", "whitebalance"),
               ("Image\nFormat", "imageformat")]
        self.pack_start(self.__create_combo_settings(cbs), False, False, 0)
        cbs = [("Drive Mode", "drivemode")]
        self.pack_start(self.__create_combo_settings(cbs), False, False, 0)
        # Camera Settings box
        internal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        internal.set_homogeneous(False)
        self.pack_start(internal, False, False, 0)
        settings = self.__create_camera_settings_box(camera)
        internal.pack_start(settings, False, False, 0)
        # Camera Properties box
        internal.pack_start(self.__create_camera_properties_box(camera.model,
                            camera.lensname), False, False, 0)

    def __create_camera_settings_box(self, camera):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box.set_homogeneous(False)
        if camera.shutterspeed_model:
            shutter = OptionSelector("Shutter", camera.shutterspeed_model)
            box.pack_start(shutter, False, False, 0)
        if camera.aperture_model:
            aperture = OptionSelector("Aperture", camera.aperture_model)
            box.pack_start(aperture, False, False, 0)
        if camera.iso_model:
            iso = OptionSelector("ISO", camera.iso_model)
            box.pack_start(iso, False, False, 0)
        return box

    def __create_combo_settings(self, settings):
        """Create UI for Wite Balance and Image Format."""
        def set_value_if(model, _, iter, name):
            value = getattr(self.camera, name)
            if model[iter][0] == value:
                getattr(self, name).set_active_iter(iter)
                return True
            else:
                return False

        def create_combo(label, name):
            model = self.camera.get_setting_model(name)
            if model is None:
                return None
            vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
            # TODO: this 3-line hack computes the alleged max label size.
            text = label_with_character_size(7)
            text.set_text(label)
            vbox.pack_start(text, False, False, 0)
            cb = ListComboBox(model)
            setattr(self, name, cb)
            cb.get_model().foreach(set_value_if, name)
            cb.connect('changed',
                       lambda combo: setattr(self.camera, name, combo.value))
            vbox.pack_start(cb, True, True, 0)
            return vbox

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for (title, cap) in settings:
            combo = create_combo(title, cap)
            if combo is not None:
                box.pack_start(combo, False, False, 0)
        return box

    def __create_camera_properties_box(self, model, lens):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        box.set_homogeneous(True)
        camera_model = Gtk.Label(label=model)
        lens_model = Gtk.Label(label=lens)
        box.pack_start(camera_model, True, False, 0)
        box.pack_start(lens_model, True, False, 0)
        return box
