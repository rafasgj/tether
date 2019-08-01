# Tether

Allows capturing images from cameras tethered to a computer USB.

You must create a "images" directory in the current directory for it to
work. I know it sucks, but, as of today, it is the way it is.

## Dependencies

Tether needs Python 3, which is easily avaiable for Linux, easily installed
on Windows, and might require the use of a package manager like Homebrew if
you have an older version of macOS (like High Sierra).

Pure Python dependencies may be installed with PIP, by issuing

```sh
python3 -m pip install -U -r requriments.txt
```

You might need to change 'python3' to 'python' depending on your operating
system and/or installation.

### GTK+ 3

As Tether uses GTK+ 3, some Python dependencies must be installed and
cannot be installed using PIP.

For Linux, most distributions have PyGObject in their main package
repositories. Under macOS, you should use Homebrew to install it.
Unfortunatelly, I don't use Windows and have no idea on how to install.

### LibRaw

If your camera provides RAW files, you will want to use it to capture the
images, and this will require that you have LibRaw installed. Anything, from
version 0.18 will do, but use the most recent available.
