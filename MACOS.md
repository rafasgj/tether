# Installation on Apple's macOS

To use Tether on macOS, you'll need to have both Python 3, GTK+, PyGobject,
and LibRaw installed on your system. All of them can be installed with
[Homebrew](https://brew.sh).

If you prefer, you can download the Python version the official
repositories at [Python.org](https://python.org/downloads).

## Installing Dependencies

### Homebrew

If you run macOS up to version 10.13 (High Sierra), your system comes with
Python 2 installed, and I recommend you to install Python 3 through
Homebrew, and you can install the other dependencies using it.

The packages that need to be installed are:

* gtk+3
* pygobject
* libgphoto2
* libraw

To install all packages run

```sh
$ brew install gtk+3 pygobject libgphoto2 libraw
```

### Other package managers

If you use other package managers like mac ports or Fink, you might
contribute to this project by writing instructions on installing the
dependencies. 
