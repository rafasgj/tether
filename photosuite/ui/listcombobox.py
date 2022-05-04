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

"""A ComboBox based on a list of values."""

from gi.repository import Gtk


class ListComboBox(Gtk.ComboBox):  # pylint: disable=too-few-public-methods
    """Create a combo box control."""

    def __init__(self, datalist):
        """Initialize object."""
        Gtk.ComboBox.__init__(self)
        datastore = Gtk.ListStore(str)
        for entry in datalist:
            datastore.append([entry])
        self.set_model(datastore)
        renderer_text = Gtk.CellRendererText()
        self.pack_start(renderer_text, True)
        self.add_attribute(renderer_text, "text", 0)
        self.set_active(0)

    @property
    def value(self):
        """Retrieve the currently selected item."""
        model = self.get_model()
        iterator = self.get_active_iter()
        return model[iterator][0]
