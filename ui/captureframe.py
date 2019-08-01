"""Creates an embedable frame with UI to capture images."""

import io
from gi.repository import Gtk, Gdk, GdkPixbuf
from ui import CameraControlBox  # noqa: E402
import PIL


class CaptureFrame(Gtk.Frame):
    """Defines an embedable frame."""

    def __init__(self, width, height, camera):
        """Initialize the frame object."""
        Gtk.Frame.__init__(self)
        self.camera = camera
        self.set_size_request(width, height)
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main.set_homogeneous(False)
        main.set_border_width(10)
        self.img_ui = Gtk.DrawingArea()
        self.img_ui.set_hexpand(True)
        self.img_ui.set_vexpand(True)
        self.image = None
        self.img_ui.connect('draw', self.__update_image_ui)
        main.pack_start(self.img_ui, True, True, 0)
        self.camera_control = CameraControlBox(camera,
                                               cb=self.camera.grab_frame)
        main.pack_end(self.camera_control, False, False, 0)
        self.add(main)

    @property
    def image(self):
        """Retrieve the currently displayed image."""
        return self.__image

    @image.setter
    def image(self, image):
        """Update displayed image."""
        if image is None:
            theme = Gtk.IconTheme.get_default()
            pixbuf = theme.load_icon("camera-photo", Gtk.IconSize.DIALOG,
                                     Gtk.IconLookupFlags.USE_BUILTIN)
            self.__image = Gtk.Image()
            self.__image.set_from_pixbuf(pixbuf)
        else:
            if isinstance(image, PIL.Image.Image):
                with io.BytesIO() as data:
                    image.save(data, "jpeg")
                    loader = GdkPixbuf.PixbufLoader.new_with_type("jpeg")
                    loader.write(data.getvalue())
                    data = loader.get_pixbuf()
                    self.__image = Gtk.Image.new_from_pixbuf(data)
                    loader.close()
            elif isinstance(image, Gtk.Image):
                self.__image = image
            else:
                raise Exception("Internal Error: Invalid image object.")
        self.img_ui.queue_draw()

    # def __update_image_ui(self, cairo_region, data):
    def __update_image_ui(self, drawing, cairo_context):
        """Update image displayed."""
        data = self.image.get_pixbuf()
        iw, ih = data.get_width(), data.get_height()
        w = self.img_ui.get_allocated_width()
        h = self.img_ui.get_allocated_height()
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
