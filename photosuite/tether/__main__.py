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
import io

from PIL import Image
from magic import Magic

import gi

gi.require_version("Gtk", "3.0")  # noqa:E702 # pylint:disable=C0321

# pylint: disable=wrong-import-position
from gi.repository import Gtk, Gdk, GdkPixbuf  # noqa: E402

from photosuite.ui.functions import button_with_icon_text  # noqa: E402
from photosuite.ui.cameracontrolbox import CameraControlBox  # noqa: E402
from photosuite.ui.filenametemplatedialog import FilenameTemplateDialog  # noqa

from photosuite.camera.camera import Camera  # noqa: E402
from photosuite.camera.gphoto2driver import GPhoto2Driver  # noqa: E402

from photosuite.util.formatter import FilenameFormatter  # noqa: E402
from photosuite.util.phexif import ExifTool  # noqa: E402

# pylint: enable=wrong-import-position


# Hold the last image captured
last_image = None  # pylint: disable=invalid-name
img_win = None  # pylint: disable=invalid-name

filename_formatter = FilenameFormatter()
mime = Magic(True)
exif = ExifTool()
exif.start()
capture_directory = os.getcwd()


def picture_taken(_camera, fname):
    """Handle new frame signal."""
    global last_image  # pylint: disable=invalid-name,global-statement
    pil = ("image/jpeg", "image/tiff", "image/gif", "image/png")
    mime_type = mime.from_file(fname)  # pylint: disable=no-member
    metadata = exif.get_metadata(fname)[0]
    key = "EXIF:Orientation"
    rotation = [0, 0, 0, 180, 0, 0, -90, 0, 90]
    orientation = rotation[int(metadata[key])] if key in metadata else 0
    if mime_type in pil:
        last_image = Image.open(fname)
    else:
        reader = io.BytesIO(exif.get_image_preview(fname))
        last_image = Image.open(reader)
    last_image = last_image.rotate(orientation, expand=True)
    img_win.queue_draw()


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
        "file_set", lambda b: camera.set_capture_directory(b.get_filename())
    )
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
    filename = camera.grab_frame(filename=filename)
    picture_taken(camera, filename)


def update_formatter(_sender, *_args):
    """Update filename formatter."""
    dialog = FilenameTemplateDialog(
        format=filename_formatter.format, transient_for=None
    )
    if dialog.run() == Gtk.ResponseType.OK:  # pylint: disable=no-member
        filename_formatter.add_keys(dialog.user_defined)
        filename_formatter.format = dialog.filename_template
    dialog.destroy()


def get_image_pixbuf(image):
    """Given the image, get its contents as a GdkPixbuf."""
    if isinstance(image, Image.Image):
        with io.BytesIO() as data:
            image.save(data, "jpeg")
            loader = GdkPixbuf.PixbufLoader.new_with_type("jpeg")
            loader.write(data.getvalue())
            data = loader.get_pixbuf()
            loader.close()
    elif isinstance(image, Gtk.Image):
        data = image.get_pixbuf()
    else:
        raise Exception("Internal Error: Invalid image object.")
    return data


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


def create_image_window():
    """Create window to display image."""
    global img_win  # pylint: disable=invalid-name, global-statement
    width, height = get_screen_dimension()
    img_win = Gtk.Window()
    img_win.connect("destroy", Gtk.main_quit)
    img_win.set_position(Gtk.WindowPosition.CENTER)
    img_win.set_title("Picture Maker")
    img_ui = Gtk.DrawingArea()
    img_ui.set_hexpand(True)
    img_ui.set_vexpand(True)
    img_ui.connect("draw", update_image_ui)
    img_win.set_size_request(int(width * 0.75), int(height * 0.75))
    img_win.add(img_ui)
    img_win.move(0, 0)
    img_win.show_all()


def update_image_ui(drawing_area, cairo_context):
    """Update image displayed."""
    if last_image is not None:
        # pylint: disable=invalid-name
        img_win.activate()
        data = get_image_pixbuf(last_image)
        iw, ih = data.get_width(), data.get_height()
        w = drawing_area.get_allocated_width()
        h = drawing_area.get_allocated_height()
        r = min(w / iw, h / ih)
        rw, rh = int(iw * r), int(ih * r)
        if w < iw or h < ih:
            interp = GdkPixbuf.InterpType.BILINEAR
            data = GdkPixbuf.Pixbuf.scale_simple(data, rw, rh, interp)
        else:
            rw, rh = iw, ih
        x, y = 0, 0
        if rw < w or rh < h:
            x = w // 2 - rw // 2
            y = h // 2 - rh // 2
        Gdk.cairo_set_source_pixbuf(cairo_context, data, x, y)
        cairo_context.paint()
        # pylint: enable=invalid-name
    return False


def display_select_folder_dialog(title, parent=None):
    """Create a dialog to select a folder."""
    buttons = (
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),
        (Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
    )
    action = Gtk.FileChooserAction.SELECT_FOLDER
    dialog = Gtk.FileChooserDialog(
        title=title, action=action, transient_for=parent
    )
    for button in buttons:
        dialog.add_button(*button)
    dialog.set_local_only(True)
    dialog.set_create_folders(True)
    dialog.set_current_folder(capture_directory)
    try:
        if dialog.run() == Gtk.ResponseType.OK:
            return dialog.get_filename()
    finally:
        dialog.destroy()
    return None


def change_target_directory(*_args):
    """Ask user for the new capture directory."""
    directory = display_select_folder_dialog("Select capture folder", win)
    if directory:
        camera.capture_directory = directory


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
    create_image_window()
    window = Gtk.Window()
    window.set_decorated(False)
    width, height = get_screen_dimension()
    window.move(width, height)
    window.connect("destroy", Gtk.main_quit)
    window.add(create_frame())
    window.show_all()
    window.set_keep_above(True)

    return window


if __name__ == "__main__":
    try:
        cameras = [p for (c, p) in GPhoto2Driver.autodetect()]
        if not cameras:
            print("No camera found.")
        else:
            port = cameras[0]
            camera = Camera(GPhoto2Driver(port))
            win = start_gui()
            Gtk.main()
    except Exception as ex:  # pylint: disable=broad-except
        import traceback

        MSG = "Is the camera correctly attached and turned on?"
        # pylint: disable=consider-using-f-string
        print("%s\n%s\n%s" % (traceback.format_exc(), ex, MSG))
        # pylint: enable=consider-using-f-string
