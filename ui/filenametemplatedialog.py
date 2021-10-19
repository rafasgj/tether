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

"""Create a filename template dialog."""

import gi

gi.require_version("Gtk", "3.0")  # noqa: E702
from gi.repository import Gtk

"""
Define an object that transform filenames using metadata.

Filename creation rules:

    A user may add new keys, like:
        {camera} - camera serial number.
        {lens} - lens serial number (not yet supported).
"""


class FilenameTemplateDialog(Gtk.Dialog):
    """Define a template that allow the definition of a filename template."""

    def __init__(self, format="", *args, **kwargs):
        """Initialize the dialog."""
        Gtk.Dialog.__init__(
            self,
            *args,
            **{k: kwargs[k] for k in kwargs if k not in ["custom_strings"]},
        )
        self.set_size_request(*(450, 300))
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
        )
        self.entries = {}
        #
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.box.set_homogeneous(False)
        frame = Gtk.Frame(label="Filename Template")
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        frame.add(self.box)
        frame.set_border_width(8)
        self.vbox.pack_start(frame, False, False, 0)
        #
        self.entry = Gtk.Entry()
        self.entry.vexpand = False
        self.entry.hexpand = True
        self.entry.set_text(format)
        self.box.pack_start(self.entry, False, False, 0)
        #
        self.add_entry("Custom Text", "custom_text")
        #
        date_strings = (
            ("4-digit Year", "{YYYY}"),
            ("2-digit Year", "{YY}"),
            ("2-digit Month", "{MM}"),
            ("Abrev. Month", "{mon}"),
            ("Month Name", "{month}"),
            ("2-digit Day", "{DD}"),
        )
        flowbox = self.__create_flow_box("Date", date_strings)
        self.box.pack_start(flowbox, False, False, 0)
        #
        seq_strings = (
            ("4-digit Sequence (0001)", "{seq:04}"),
            ("3-digit Sequence (001)", "{seq:03}"),
            ("2-digit Sequence (01)", "{seq:02}"),
            ("1-digit Sequence (1)", "{seq}"),
        )
        flowbox = self.__create_flow_box("Sequence Counter", seq_strings)
        self.box.pack_start(flowbox, False, False, 0)
        #
        file_strings = (
            ("Original Filename", "{filename}"),
            ("Lowercase Extension", "{ext}"),
            ("Uppercase Extension", "{EXT}"),
            ("Original Full Filename", "{original}"),
        )
        flowbox = self.__create_flow_box("Filename", file_strings)
        self.box.pack_start(flowbox, False, False, 0)
        #
        custom_strings = kwargs.get("custom_strings", None)
        if custom_strings is not None:
            flowbox = self.__create_flow_box("Custom", custom_strings)
            self.box.pack_start(flowbox, False, False, 0)
        #
        self.show_all()

    @property
    def filename_template(self):
        """Retrieve the currently set filename template."""
        return self.entry.get_text()

    @property
    def user_defined(self):
        """Retrieve a dictionary with all user defined values."""
        return self.entries

    def __text_changed(self, entry, name):
        self.entries[name] = entry.get_text()

    def __add_text(self, button, entry, text):
        old_text = entry.get_text()
        bounds = entry.get_selection_bounds()
        if bounds:
            start, end = bounds
        else:
            start = entry.get_position()
            end = start

        entry.set_text(old_text[:start] + text + old_text[end:])
        entry.set_position(start + len(text))
        entry.grab_focus_without_selecting()
        return False

    def add_entry(self, title, field):
        """Add an entry box to the dialog."""
        self.entries[field] = ""
        sbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        sbox.set_homogeneous(False)
        entry = Gtk.Entry()
        entry.vexpand = False
        entry.hexpand = True
        entry.connect("changed", self.__text_changed, field)

        label = Gtk.Label(label=title)
        label.set_xalign(0.0)
        sbox.pack_start(label, False, False, 0)
        sbox.pack_start(entry, True, True, 0)

        button = Gtk.Button(label="Insert")
        text_to_add = "{{{}}}".format(field)
        button.connect("clicked", self.__add_text, self.entry, text_to_add)
        sbox.pack_start(button, False, False, 0)
        self.box.pack_start(sbox, False, False, 0)

    def __create_flow_box(self, title, itemlist):
        """Create a flowbox with a list of itens."""
        iframe = Gtk.Frame(label=" {} ".format(title))
        iframe.set_border_width(0)
        iframe.set_label_align(0.02, 0.5)
        sbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        iframe.add(sbox)
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(8)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_homogeneous(False)
        for text, insert in itemlist:
            button = Gtk.Button(label=text)
            button.connect("clicked", self.__add_text, self.entry, insert)
            flowbox.add(button)
        sbox.pack_start(flowbox, False, False, 0)
        return iframe
