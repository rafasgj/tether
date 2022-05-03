# Installation on Apple's macOS

To use Tether on macOS, you'll need GTK+ and PyGobject installed on your
system, and can be installed using `pip`. If you encounter any issue, use
[Homebrew](https://brew.sh). Make sure to use at least version 3.42.1 of
PyGobject.

As Python 3 is required, on older systems up to macOS Catalina (10.15)
you'll need to install Python 3 from an external package manager (like
Homebrew). Starting on macOS Big Sur (11.0), Python 3 is already part
of the command line tools.

Install `Tether` and its dependencies with:

```sh
% python3 -m venv /tmp/venv
% . /tmp/venv/bin/activate
% pip install -e .\[dev\]
```

> NOTE: The utility that monitors a directory to display captured images
is not working in macOS.
