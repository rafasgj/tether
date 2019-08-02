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
from PIL import Image

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk    # noqa: E402
from ui import CaptureFrame    # noqa: E402


def picture_taken(camera, filename):
    """Handle new frame signal."""
    global camera_frame
    try:
        # Try JPEG or TIFF
        camera_frame.image = Image.open(filename)
    except Exception as ex:
        # If it fails, try RAW.
        camera_frame.image = image_from_raw(filename)


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
                win = Gtk.Window()
                win.set_title("Picture Maker")
                win.connect("destroy", Gtk.main_quit)
                camera_frame = CaptureFrame(800, 600, camera)
                fn = camera.grab_frame
                camera_frame.camera_control.set_shutter_function(fn)
                win.add(camera_frame)
                win.show_all()

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
                if response == Gtk.ResponseType.OK:
                    camera.capture_directory = dialog.get_filename()
                    dialog.destroy()
                    Gtk.main()
    except Exception as ex:
        print(ex)
        if camera is not None and camera.last_error is None:
            print("Is the camera correctly attached and turned on?  ")
