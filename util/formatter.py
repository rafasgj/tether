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

    def __init__(self, rename_rule="IMG_{seq:04}.{EXT}", **kwargs):
        """Initialize filename formater."""
        self.format = rename_rule
        self.counter = kwargs.get('initial', 0)
        self.date = kwargs.get('date', datetime.datetime.now())
        self.format_set = {
            "custom_text": kwargs.get('text', ''),
            "seq": 0,
            "filename": "",
            "ext": "",
            "EXT": ""
        }
        self.__filldate()

    def __filldate(self):
        date = {
            "YYYY": self.date.strftime("%Y"),
            "YY":  self.date.strftime("%y"),
            "MM":  self.date.strftime("%m"),
            "mon":  self.date.strftime("%b"),
            "month":  self.date.strftime("%B"),
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

    def filename(self, original, **kwargs):
        """Format the filename given the current rules."""
        self.counter += 1
        self.set('seq', self.counter)
        self.__filldate()
        (filename, ext) = os.path.splitext(original)
        self.set('ext', ext[1:].lower())
        self.set('EXT', ext[1:].upper())
        self.set('filename', os.path.basename(filename))
        self.set('original', os.path.basename(original))
        for key, value in kwargs.items():
            self.set(key, value)
        return self.format.format(**self.format_set)

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, value):
        self._counter = value

    @property
    def keys(self):
        """Query the currently stored keys in the formatter."""
        return self.format_set.keys()
