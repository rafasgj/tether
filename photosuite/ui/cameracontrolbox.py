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

"""Define the UI to control camera settings."""

from gi.repository import Gtk
from .optionselector import OptionSelector  # pylint: disable=import-error


class CameraControlBox(Gtk.Box):
    """Create box to control camera settings."""

    def __init__(self, camera, _cb=None):
        """Initialize the UI composed component."""
        Gtk.Box.__init__(
            self, orientation=Gtk.Orientation.HORIZONTAL, spacing=10
        )
        self.set_homogeneous(False)
        self.camera = camera
        internal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        internal.set_homogeneous(False)
        self.pack_start(internal, False, False, 0)  # pylint: disable=no-member
        settings = self.__create_camera_settings_box(camera)
        internal.pack_start(settings, False, False, 0)

    def __create_camera_settings_box(self, camera):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        # box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box.set_homogeneous(False)
        models = (
            ("Shutter", "shutterspeed"),
            ("Aperture", "aperture"),
            ("ISO", "iso"),
        )
        for title, model in models:
            selector = OptionSelector(title, camera.models.get(model))
            setattr(self, model, selector)
            box.pack_start(selector, False, False, 0)
        return box
