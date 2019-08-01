"""Define the UI for a single camera setting."""

from gi.repository import Gtk


class CameraSettingCombo(Gtk.ComboBox):
    """Create a combo box control."""

    def __init__(self, model):
        """Initialize object."""
        Gtk.ComboBox.__init__(self)
        datastore = Gtk.ListStore(str)
        for entry in model:
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


class CameraSettingBox(Gtk.Box):
    """A compose widget for setting camera values."""

    def __init__(self, title, model):
        """Initialize the object."""
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.model = model
        self.title = title
        self.current = 0
        self.set_homogeneous(False)
        label = Gtk.Label()
        label.set_markup("<b>{}</b>".format(title))
        self.pack_start(label, False, False, 0)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box.set_homogeneous(False)
        less = Gtk.Button()
        less.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.LEFT,
                           shadow_type=Gtk.ShadowType.NONE))
        less.connect("clicked", self.decrease_value)
        self.label = Gtk.Label()
        # TODO: this 4-line hack computes the alleged max label size.
        sz = Gtk.Label(label="4444444")
        sz.show()
        sz = sz.size_request()
        self.label.set_size_request(sz.width, sz.height)
        self.__update_label()
        more = Gtk.Button()
        more.connect("clicked", self.increase_value)
        more.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.RIGHT,
                           shadow_type=Gtk.ShadowType.NONE))
        box.pack_start(less, False, False, 0)
        box.pack_start(self.label, False, False, 0)
        box.pack_start(more, False, False, 0)
        self.pack_start(box, False, False, 0)

    def increase_value(self, button):
        """Advance to next setting value."""
        self.model.increase_value()
        self.__update_label()

    def decrease_value(self, button):
        """Advance to next setting value."""
        self.model.decrease_value()
        self.__update_label()

    def __update_label(self):
        self.label.set_markup("<b>{}</b>".format(self.model.value))
