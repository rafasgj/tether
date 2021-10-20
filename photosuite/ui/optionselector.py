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

"""Define the UI for a single camera setting."""

from gi.repository import Gtk

from .functions import label_with_character_size  # pylint: disable=import-error


class OptionSelector(Gtk.Box):
    """A compose widget for setting camera values."""

    def __init__(self, title, datalist):
        """Initialize the object."""
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.model = datalist
        self.title = title
        self.current = 0
        self.set_homogeneous(False)
        label = Gtk.Label()
        label.set_markup(f"<b>{title}</b>")
        self.pack_start(label, False, False, 0)  # pylint: disable=no-member
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.set_homogeneous(False)
        self.label = label_with_character_size(6)
        self.__update_label()
        button = self.__button(Gtk.ArrowType.LEFT, self.__decrease_value)
        box.pack_start(button, False, False, 0)
        box.pack_start(self.label, False, False, 0)
        button = self.__button(Gtk.ArrowType.RIGHT, self.__increase_value)
        box.pack_start(button, False, False, 0)
        self.pack_start(box, False, False, 0)  # pylint: disable=no-member

    @staticmethod
    def __button(arrow, handler):
        button = Gtk.Button()
        button.connect("clicked", handler)
        shadow = Gtk.ShadowType.NONE
        button.add(Gtk.Arrow(arrow_type=arrow, shadow_type=shadow))
        return button

    def __increase_value(self, _sender):
        """Advance to next setting value."""
        self.model.next()
        self.__update_label()

    def __decrease_value(self, _sender):
        """Advance to next setting value."""
        self.model.previous()
        self.__update_label()

    def __update_label(self):
        self.label.set_markup(f"<b>{self.model.value}</b>")
