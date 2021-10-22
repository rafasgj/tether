# Installation on Apple's macOS

To use Tether on macOS, you'll need GTK+, PyGobject, and
exiftool installed on your system. All of them can be installed with
[Homebrew](https://brew.sh).

As Python 3 is required, on older systems, up to macOS Catalina (10.15),
you'll need to install Python 3 from an external package manager (like
Homebrew). Starting on macOS Big Sur (11.0), Python 3 is already part
of the command line tools.

If you prefer, you can download the Python version from the official
repositories at [Python.org](https://python.org/downloads).

## Installing Dependencies

The packages that need to be installed are:

* gtk+3
* pygobject
* libgphoto2
* libmagic

To install all packages run

```sh
$ brew install gtk+3 pygobject libgphoto2 libraw libmagic
```
