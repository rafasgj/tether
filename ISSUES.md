# ISSUES

This software is in its early stages of development, and there are certainly
many issues with it.

It has only been tested with the cameras Canon 6D mark I, Canon 7D mark I,
Canon XTi/400D, Olympus e-Pen EP-2 and Olympus OM-D E-10 mark I, and only the
Canons are supported (as it should be, due to GPhoto2 limitations). So, there's
a good chance that your camera won't work.

If you are not able to make your camera to work, please, open an issue
[on Github](https://github.com/rafasgj/tether/issues), providing, at least:

    * Your camera brand and model.
    * The Python version used..
    * The GPhoto2 version used.
    * The Linux distro vendor and version.

It might help to provide your GTK+ version, and kernel version, but they should
not matter (until we find they do).

## Known Issues

These are known issues and some fixes for them.

1. Console shows `GVFS-RemoteVolumeMonitor-WARNING **: remote volume monitor
with dbus name org.gtk.vfs.UDisks2VolumeMonitor is not supported`

 > This happened with Fedora 27, and there are reports on other **systemd**
 systems  that it also happen with other programs. To stop this warning from
 being issued run `systemctl --user restart gvfs-udisks2-volume-monitor`. The
 Remote Volume Monitor is used to block saving captured images to remote disks.
 You should backup on remote disks, but not use them to capture and edit photos.

