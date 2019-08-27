"""Define the UI for a single camera setting."""

from gi.repository import Gtk

from .functions import label_with_character_size


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
        label.set_markup("<b>{}</b>".format(title))
        self.pack_start(label, False, False, 0)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.set_homogeneous(False)
        self.label = label_with_character_size(6)
        self.__update_label()
        button = self.__button(Gtk.ArrowType.LEFT, self.__decrease_value)
        box.pack_start(button, False, False, 0)
        box.pack_start(self.label, False, False, 0)
        button = self.__button(Gtk.ArrowType.RIGHT, self.__increase_value)
        box.pack_start(button, False, False, 0)
        self.pack_start(box, False, False, 0)

    def __button(self, arrow, handler):
        button = Gtk.Button()
        button.connect("clicked", handler)
        shadow = Gtk.ShadowType.NONE
        button.add(Gtk.Arrow(arrow_type=arrow, shadow_type=shadow))
        return button

    def __increase_value(self, button):
        """Advance to next setting value."""
        self.model.next()
        self.__update_label()

    def __decrease_value(self, button):
        """Advance to next setting value."""
        self.model.previous()
        self.__update_label()

    def __update_label(self):
        self.label.set_markup("<b>{}</b>".format(self.model.value))
