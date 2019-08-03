"""A ComboBox based on a list of values."""

from gi.repository import Gtk


class ListComboBox(Gtk.ComboBox):
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
        iter = self.get_active_iter()
        return model[iter][0]

    @value.setter
    def value(self, value):
        """Retrieve the currently selected item."""
        model = self.get_model()
        iter = self.get_active_iter()
        return model[iter][0]
