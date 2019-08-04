"""Create a filename template dialog."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: F401

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
        Gtk.Dialog.__init__(self, *args, **kwargs)
        self.set_size_request(*(450, 300))
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
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
        # TODO: Replace selected text.
        # TODO: Position cursor at the end of the text
        new = entry.get_text()
        entry.set_text(new + text)
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
        button.connect('clicked', self.__add_text, self.entry, text_to_add)
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
            button.connect('clicked', self.__add_text, self.entry, insert)
            flowbox.add(button)
        sbox.pack_start(flowbox, False, False, 0)
        return iframe


if __name__ == "__main__":
    from util.formatter import FilenameFormatter
    custom_list = (
        ("Camera Model", '{model}'),
        ("Lens Model", '{lens}'),
        ("Camera Serial Number", '{camera_serial}')
    )
    dialog = Gtk.Window()
    x = FilenameTemplateDialog(title="Create Filename Template",
                               transient_for=dialog)
    ok = x.run()
    formatter = FilenameFormatter(format=x.filename_template)
    formatter.add_keys(x.user_defined)
    dialog.connect("destroy", Gtk.main_quit)
    dialog.show_all()
    print("Filename:", formatter.filename("image.jpg"))
