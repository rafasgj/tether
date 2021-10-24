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

"""Use a camera tethered to the device."""

import os

import gi

gi.require_version("Gtk", "3.0")  # noqa:E702 # pylint:disable=C0321

# pylint: disable=wrong-import-position, import-error
from gi.repository import Gtk, Gdk  # noqa: E402

from photosuite.ui.functions import button_with_icon_text  # noqa: E402
from photosuite.ui.cameracontrolbox import CameraControlBox  # noqa: E402
from photosuite.ui.filenametemplatedialog import FilenameTemplateDialog  # noqa

from photosuite.camera.camera import Camera  # noqa: E402
from photosuite.camera.gphoto2driver import GPhoto2Driver  # noqa: E402

from photosuite.util.formatter import FilenameFormatter  # noqa: E402

# pylint: enable=wrong-import-position, import-error


filename_formatter = FilenameFormatter()
capture_directory = os.getcwd()


def create_frame(size=(640, 80)):
    """Create the main window frame."""
    frame = Gtk.Frame()
    frame.set_size_request(*size)
    main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    main.set_homogeneous(False)
    main.set_border_width(10)

    sub = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    butns = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    button = button_with_icon_text("insert-text", "Naming Rule")
    button.connect("clicked", update_formatter)
    butns.pack_start(button, False, False, 0)
    action = Gtk.FileChooserAction.SELECT_FOLDER
    button = Gtk.FileChooserButton(title="Directory", action=action)
    button.connect(
        "file_set", lambda b: change_target_directory(b.get_filename())
    )
    button.set_local_only(True)
    button.set_create_folders(True)
    button.set_current_folder(capture_directory)
    butns.pack_end(button, False, False, 0)
    sub.pack_start(butns, False, False, 0)
    camera_control = CameraControlBox(camera, camera.grab_frame)
    sub.pack_start(camera_control, False, False, 0)
    button = button_with_icon_text(
        "camera-photo",
        "Shot!",
        Gtk.Orientation.VERTICAL,
        size=Gtk.IconSize.DIALOG,
    )
    button.connect("clicked", grab_picture)
    sub.pack_end(button, False, False, 0)
    main.pack_start(sub, False, False, 0)
    frame.add(main)
    return frame


def grab_picture(_sender):
    """Format filename and grab picture from camera."""
    filename = filename_formatter.filename("image.cr2")
    camera.grab_frame(filename=os.path.join(capture_directory, filename))


def update_formatter(_sender, *_args):
    """Update filename formatter."""
    dialog = FilenameTemplateDialog(
        format=filename_formatter.format, transient_for=None
    )
    if dialog.run() == Gtk.ResponseType.OK:  # pylint: disable=no-member
        filename_formatter.add_keys(dialog.user_defined)
        filename_formatter.format = dialog.filename_template
    dialog.destroy()


def get_screen_dimension():
    """Retrieve current screen dimension, in pixels."""
    display = Gdk.Display.get_default()
    geoms = [
        display.get_monitor(i).get_geometry()
        for i in range(display.get_n_monitors())
    ]

    width = max(r.x + r.width for r in geoms) - min(r.x for r in geoms)
    height = max(r.y + r.height for r in geoms) - min(r.y for r in geoms)

    return width, height


def change_target_directory(newdir):
    """Ask user for the new capture directory."""
    global capture_directory
    capture_directory = newdir or os.getcwd()


def set_application_theme():
    """Load application theme CSS."""
    css = b""
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(css)
    context = Gtk.StyleContext()
    screen = Gdk.Screen.get_default()
    priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    context.add_provider_for_screen(screen, css_provider, priority)


def start_gui():
    """Start graphical interface."""
    set_application_theme()
    window = Gtk.Window()
    window.set_title("Tether")
    width, height = get_screen_dimension()
    window.move(width, height)
    window.connect("destroy", Gtk.main_quit)
    window.add(create_frame())
    window.show_all()
    window.set_keep_above(True)

    return window


def camera_select(camera_list):
    """Display image to select camera from a list."""

    def on_ok(_):
        """Set the selected camera."""
        nonlocal selected, combo
        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        selected = model[tree_iter][1]
        Gtk.main_quit()

    def update_combo(camdata):
        """Update camera list."""
        nonlocal combo
        data = Gtk.ListStore(str, str)
        for cam in camdata:
            data.append(cam)
        if not combo:
            combo = Gtk.ComboBox.new_with_model(data)
            combo.set_active(0)
            renderer_text = Gtk.CellRendererText()
            combo.pack_start(renderer_text, True)
            combo.add_attribute(renderer_text, "text", 0)
        else:
            combo.set_model(data)
            combo.set_active(0)

    def refresh(_):
        update_combo(GPhoto2Driver.autodetect())

    combo = None
    selected = None
    set_application_theme()
    update_combo(camera_list)
    window = Gtk.Window()
    window.set_title("Camera")
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    vbox.set_homogeneous(True)
    window.add(vbox)
    label = Gtk.Label(label="Select Camera")
    vbox.pack_start(label, True, True, 0)
    vbox.pack_start(combo, True, True, 0)
    bok = Gtk.Button(label="Ok")
    bok.connect("clicked", on_ok)
    brefresh = Gtk.Button(label="Refresh")
    brefresh.connect("clicked", refresh)
    bcancel = Gtk.Button(label="Cancel")
    bcancel.connect("clicked", Gtk.main_quit)
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    hbox.set_homogeneous(True)
    hbox.pack_start(bcancel, True, True, 5)
    hbox.pack_start(bok, True, True, 5)
    hbox.pack_start(brefresh, True, True, 5)
    vbox.pack_start(hbox, False, False, 5)
    window.show_all()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()
    return selected


if __name__ == "__main__":
    try:
        cameras = GPhoto2Driver.autodetect()
        if len(cameras) == 1:
            port = cameras[0][1]
        else:
            port = camera_select(cameras)  # pylint: disable=invalid-name
        if not port:
            print("No camera found or selected.")
        else:
            camera = Camera(GPhoto2Driver(port))
            win = start_gui()
            Gtk.main()
    except Exception as ex:  # pylint: disable=broad-except
        import traceback

        MSG = "Is the camera correctly attached and turned on?"
        # pylint: disable=consider-using-f-string
        print("%s\n%s\n%s" % (traceback.format_exc(), ex, MSG))
