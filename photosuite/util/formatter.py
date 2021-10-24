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

"""Define an object that can create filenames based on rules."""

import os.path
import datetime


class FilenameFormatter:
    """
    Define an object that transform filenames using metadata.

    Filename creation rules:
        {text} - A custom text name.
        {YYYY} - four digit year.
        {YY} - two digit year.
        {MM} - two digit month.
        {month} - month name.
        {mon} - month name abreviatted.
        {DD} - two digit day.
        {seq:0N} - a N digit sequence counter. The initial number can be set.
        {original} - original full filename.
        {filename} - original filename. without extension.
        {ext} - original file extension, lowercase.
        {EXT} - original file extension, uppercase.

        A user may add new keys, like:
            {camera} - camera serial number.
            {lens} - lens serial number.
            {session} - the name of the current session.
    """

    def __init__(self, rename_rule="{original}", **kwargs):
        """Initialize filename formater."""
        self.rename_rule = rename_rule
        self.counter = kwargs.get("initial", 0)
        self.date = kwargs.get("date", datetime.datetime.now())
        self.format_set = {
            "custom_text": kwargs.get("text", ""),
            "seq": 0,
            "filename": "",
            "ext": "",
            "EXT": "",
        }
        self.__filldate()

    def __filldate(self):
        date = {
            "YYYY": self.date.strftime("%Y"),
            "YY": self.date.strftime("%y"),
            "MM": self.date.strftime("%m"),
            "mon": self.date.strftime("%b"),
            "month": self.date.strftime("%B"),
            "DD": self.date.strftime("%d"),
        }
        self.format_set.update(date)

    def set(self, key, value):
        """Add or modify an existing filename formatter key."""
        if value is None or str(value) is None:
            raise Exception("Invalid value for filename key.")
        self.format_set[key] = value

    def add_keys(self, keys):
        """Add several key-value pairs to the filename formatter."""
        self.format_set.update(keys)

    def get_filename(self, original, **kwargs):
        """Format the filename given the current rules."""
        self.counter += 1
        self.set("seq", self.counter)
        self.__filldate()
        (fname, ext) = os.path.splitext(original)
        self.set("ext", ext[1:].lower())
        self.set("EXT", ext[1:].upper())
        self.set("filename", os.path.basename(fname))
        self.set("original", os.path.basename(original))
        for key, value in kwargs.items():
            self.set(key, value)
        return self.rename_rule.format(**self.format_set)

    @property
    def filename(self):
        """Retrieve the next filename."""
        return self.get_filename("")

    @property
    def counter(self):
        """Retrieve current sequence counter."""
        return self._counter

    @counter.setter
    def counter(self, value):
        """Set sequence counter."""
        self._counter = value

    @property
    def keys(self):
        """Query the currently stored keys in the formatter."""
        return self.format_set.keys()
