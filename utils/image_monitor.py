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

"""Monitors a directory and display new images."""

import sys
import time
import io
from queue import Queue
from threading import Thread

# pylint: disable=import-error
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# pylint: enable=import-error

from PIL import Image
from magic import Magic

import gi

gi.require_version("Gtk", "3.0")

# pylint: disable=wrong-import-position
from gi.repository import Gtk, Gdk, GdkPixbuf  # noqa F402

from photosuite.util.phexif import ExifTool  # noqa: E402

# pylint: enable=wrong-import-position


queue = Queue()
last_image = None  # pylint: disable=invalid-name
img_win = None  # pylint: disable=invalid-name

mime = Magic(True)
exif = ExifTool()
exif.start()


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


def create_image_window():
    """Create window."""
    width, height = 1024, 768
    _win = Gtk.Window()
    _win.connect("destroy", Gtk.main_quit)
    _win.set_position(Gtk.WindowPosition.CENTER)
    _win.set_title("Picture Viewer")
    _ui = Gtk.DrawingArea()
    _ui.set_hexpand(True)
    _ui.set_vexpand(True)
    _ui.connect("draw", update_image_ui)
    _win.set_size_request(int(width * 0.75), int(height * 0.75))
    _win.add(_ui)
    _win.show_all()
    return _win


def picture_taken(fname):
    """Handle new frame signal."""
    global last_image  # pylint: disable=invalid-name,global-statement
    pil = ("image/jpeg", "image/tiff", "image/gif", "image/png")
    mime_type = mime.from_file(fname)  # pylint: disable=no-member
    if mime_type.startswith("image/"):
        try:
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
        except Exception as exception:  # pylint: disable=broad-except
            print(
                f"Failed to display image {fname} ({mime_type}).\n"
                + f"Error: {str(exception)}"
            )


class FileThread(Thread):
    """Thread that handles filesystem events."""

    def __init__(self):
        """Initialie thread object."""
        super().__init__()
        self.keep_running = False

    def start(self):
        """Start running thread."""
        self.keep_running = True
        super().start()

    def run(self):
        """Thread entry point."""
        while self.keep_running:
            while queue.empty() and self.keep_running:
                time.sleep(1)
            if self.keep_running:
                file, closed = queue.get()
                if closed:
                    picture_taken(file)
                queue.task_done()

    def stop(self):
        """Stop running thread."""
        self.keep_running = False
        queue.join()


class MonitorEvent(FileSystemEventHandler):
    """Implement file system event hander."""

    # pylint: disable=too-few-public-methods
    def on_closed(self, event):  # pylint: disable=no-self-use
        """On closed event."""
        if not event.is_directory:
            queue.put((event.src_path, True))


if __name__ == "__main__":
    PATH = sys.argv[1] if len(sys.argv) > 1 else "."

    img_win = create_image_window()

    thread = FileThread()
    thread.start()

    observer = Observer()
    observer.schedule(MonitorEvent(), PATH, recursive=True)
    observer.start()
    try:
        Gtk.main()
    finally:
        observer.stop()
        observer.join()
        thread.stop()
