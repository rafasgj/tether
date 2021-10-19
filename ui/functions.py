"""Functions that didn't fit anywhere else."""

from gi.repository import Gtk


def label_with_character_size(size):
    """Create a label with a size defined by the number of characters."""
    label = Gtk.Label()
    # TODO: this 4-line hack computes the alleged max label size.
    sz = Gtk.Label(label="W" * size)
    sz.show()
    sz = sz.size_request()
    label.set_size_request(sz.width, sz.height)
    return label


def button_with_icon_text(
    icon, text, orientation=Gtk.Orientation.HORIZONTAL, size=Gtk.IconSize.BUTTON
):
    """Create a butto with icon and text."""
    button_box = Gtk.Box(orientation=orientation, spacing=3)
    button_box.set_homogeneous(False)
    img = Gtk.Image()
    img.set_from_icon_name(icon, size)
    img.set_hexpand(False)
    label = Gtk.Label()
    label.set_hexpand(True)
    label.set_markup(text)
    button_box.pack_start(img, False, False, 0)
    button_box.pack_end(label, False, False, 0)
    button = Gtk.Button()
    button.set_always_show_image(True)
    button.add(button_box)
    button.set_hexpand(False)
    button.set_vexpand(False)
    return button
