"""Define an object that can create filenames based on rules."""

import os.path
import datetime


class FilenameFormatter:
    """
    Define an object that transform filenames using metadata.

    Filename creation rules:
        {session} - The session name.
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
            {lens} - lens serial number (not yet supported).
    """

    def __init__(self, format="IMG_{seq:04}.{EXT}",
                 session="", text="", initial=0):
        """Initialize filename formater."""
        self.format = format
        self.counter = initial
        self.format_set = {
            "session": session,
            "text": text,
            "seq": 0,
            "filename": "",
            "ext": "",
            "EXT": ""
        }
        self.__filldate()

    def __filldate(self):
        today = datetime.datetime.now()
        date = {
            "YYYY": today.strftime("%Y"),
            "YY":  today.strftime("%y"),
            "MM":  today.strftime("%m"),
            "mon":  today.strftime("%b"),
            "month":  today.strftime("%B"),
            "DD": today.strftime("%d"),
        }
        self.format_set.update(date)

    def set(self, key, value):
        """Add or modify an existing filename formatter key."""
        if value is None or str(value) is None:
            raise Exception("Invalid value for filename key.")
        self.format_set[key] = value

    def filename(self, original):
        """Format the filename given the current rules."""
        self.counter += 1
        self.set('seq', self.counter)
        self.__filldate()
        (filename, ext) = os.path.splitext(original)
        self.set('ext', ext[1:].lower())
        self.set('EXT', ext[1:].upper())
        self.set('filename', os.path.basename(filename))
        self.set('original', os.path.basename(original))
        return self.format.format(**self.format_set)
