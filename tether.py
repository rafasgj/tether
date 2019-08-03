"""Use a camera tethered to the device."""

# TODO:
# whitebalance icons and UI
# focusmode UI
# drivemode icons and UI
# imageformat setting UI
#
# Manual focus drive\

from camera import Camera
from rawconverter import image_from_raw

import os
import PIL
import io

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf    # noqa: E402
from ui.functions import button_with_icon_text    # noqa: E402
from ui.cameracontrolbox import CameraControlBox  # noqa: E402


# Hold the last image captured
last_image = None


def picture_taken(camera, filename):
    """Handle new frame signal."""
    global last_image
    try:
        # Try JPEG or TIFF
        last_image = PIL.Image.open(filename)
    except Exception as ex:
        # If it fails, try RAW.
        last_image = image_from_raw(filename)


def set_application_theme():
    """Load application theme CSS."""
    css = b''
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(css)
    context = Gtk.StyleContext()
    screen = Gdk.Screen.get_default()
    priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    context.add_provider_for_screen(screen, css_provider, priority)


def create_frame(size=(640, 480)):
    """Create the main window frame."""
    frame = Gtk.Frame()
    frame.set_size_request(*size)
    main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    main.set_homogeneous(False)
    main.set_border_width(10)
    img_ui = Gtk.DrawingArea()
    img_ui.set_hexpand(True)
    img_ui.set_vexpand(True)
    img_ui.connect('draw', update_image_ui)
    main.pack_start(img_ui, True, True, 0)

    sub = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    butns = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    button = button_with_icon_text("insert-text", "Rename")
    button.connect('clicked', lambda button: print("Rename Clicked."))
    butns.pack_start(button, False, False, 0)
    button = button_with_icon_text("folder", "Directory")
    button.connect('clicked', change_target_directory)
    butns.pack_start(button, False, False, 0)
    sub.pack_start(butns, False, False, 0)
    camera_control = CameraControlBox(camera, camera.grab_frame)
    sub.pack_start(camera_control, False, False, 0)
    button = button_with_icon_text("camera-photo", 'Shot!',
                                   Gtk.Orientation.VERTICAL,
                                   size=Gtk.IconSize.DIALOG)
    button.connect('clicked', camera.grab_frame)
    sub.pack_end(button, False, False, 0)
    main.pack_start(sub, False, False, 0)
    frame.add(main)
    return frame


def get_image_pixbuf(image):
    """Given the image, get its contents as a GdkPixbuf."""
    if isinstance(image, PIL.Image.Image):
        with io.BytesIO() as data:
            image.save(data, "jpeg")
            loader = GdkPixbuf.PixbufLoader.new_with_type("jpeg")
            loader.write(data.getvalue())
            data = loader.get_pixbuf()
            loader.close()
            img = Gtk.Image.new_from_pixbuf(data)
    elif isinstance(image, Gtk.Image):
        img = image
    else:
        raise Exception("Internal Error: Invalid image object.")
    return img.get_pixbuf()


def update_image_ui(drawing_area, cairo_context):
    """Update image displayed."""
    if last_image is not None:
        data = get_image_pixbuf(last_image)
        iw, ih = data.get_width(), data.get_height()
        w = drawing_area.get_allocated_width()
        h = drawing_area.get_allocated_height()
        r = min(w/iw, h/ih)
        rw, rh = int(iw*r), int(ih*r)
        if w < iw or h < ih:
            interp = GdkPixbuf.InterpType.BILINEAR
            data = GdkPixbuf.Pixbuf.scale_simple(data, rw, rh, interp)
        else:
            rw, rh = iw, ih
        x, y = 0, 0
        if rw < w or rh < h:
            x = w//2 - rw//2
            y = h//2 - rh//2
        Gdk.cairo_set_source_pixbuf(cairo_context, data, x, y)
        cairo_context.paint()
    return False


def change_target_directory(*args):
    """Ask user for the new capture directory."""
    buttons = ((Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),
               (Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    title = "Select capture folder"
    action = Gtk.FileChooserAction.SELECT_FOLDER
    dialog = Gtk.FileChooserDialog(title=title, action=action,
                                   transient_for=win)
    for button in buttons:
        dialog.add_button(*button)
    dialog.set_local_only(True)
    dialog.set_create_folders(True)
    dialog.set_current_folder(os.getcwd())
    response = dialog.run()
    directory = dialog.get_filename()
    dialog.destroy()
    if response == Gtk.ResponseType.OK:
        camera.capture_directory = directory
        return True
    else:
        return False


if __name__ == "__main__":
    camera = None
    try:
        cameras = [p for (c, p) in Camera.autodetect() if "PTP mode" not in c]
        if not cameras:
            print("No camera found.")
        else:
            port = cameras[0]
            camera = Camera(port, "images")
            camera.on_frame_grab(picture_taken)
            if camera.last_error:
                print("Error initializing camera.")
                print(camera.last_error)
                camera.reset_error()
            else:
                set_application_theme()
                win = Gtk.Window()
                win.set_title("Picture Maker")
                win.connect("destroy", Gtk.main_quit)

                win.add(create_frame())
                win.show_all()
                if change_target_directory():
                    Gtk.main()
    except Exception as ex:
        import traceback
        print(traceback.format_exc())
        print(ex)
        if camera is not None and camera.last_error is None:
            print("Is the camera correctly attached and turned on?  ")