# Tether

A GUI to capture images from cameras tethered to a computer USB.

If something seem to be wrong, it probably is, but check
[ISSUES.md](ISSUES.md) before reporting
[on Github](https://github.com/rafasgj/tether/issues).

## Dependencies

### Libgphoto2

Gphoto2 is composed of a command-line utility and a shared library with
functions that allow controlling a camera connected to the computer. It
must be installed, before the Python modules. Use the latest available
for your package manager. You will also need the development files for
libgphoto2 (libgphoto2-devel or libgphoto2-dev) and the Python
header files available (from package python3-devel or python3-dev).

### Python Modules

Tether needs **Python 3**, which is easily avaiable for Linux, easily
installed on Windows, and might require the use of a package manager
like [Homebrew](https://brew.sh) if you have an older version of macOS
(like High Sierra).

Pure Python dependencies may be installed with PIP, by issuing

```sh
python3 -m pip install -U -r requriments.txt
```

You might need to change 'python3' to 'python' depending on your
operating system and/or installation.

### GTK+ 3

Under Python, GTK+ 3 implementations uses GObject instrospection, and
it must be available before installyng pygobject.

For Linux, most distributions have PyGObject in their main package
repositories, but I recommend installing the dependencies through the
package manager, and pygobject through PIP.

The following development packages are required to install PyGObject:
	* cairo
	* gobject-introspection
	* cairo-gobject

Under macOS, you should use Homebrew to install it. Unfortunatelly,
I don't use Windows and have no idea on how to install GTK+ on it.

### LibRaw

If your camera provides RAW files, you will want to use it to capture the
images, and this will require that you have LibRaw installed. Anything,
from version 0.18 will do, but use the most recent available.

### LibMagic

It is used to identify which type of image is to be captured from
camera and displayed. You probably have it installed on your Linux
machine, you might need to install it under other operating systems.

### ExifTool

Phil Harvey's ExifTool is an amazing tool to deal with image EXIF
metadata, and is used to extract embedded images from RAW files.
This is much faster than applying a demosaic algorithm to the RAW
files, and provide a similar view than the camera LCD monitor.

### Indirect Dependencies

This software has some dependencies that might help on its use, but are
not mandatory. These dependencies often show as optional dependencies of
libraries and components used.

* Gnome Virtual File System - gvfs
* Udisks2
