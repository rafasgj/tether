#!/bin/sh

linux_dependencies() {
	. /etc/os-release
	case $NAME in
		"Fedora")
			gphoto="libgphoto2 libgphoto2-devel python3-devel"
			gtk="cairo-devel gobject-introspection-devel"
			exif="perl-Image-ExifTool"
			dnf install $gphoto $gtk $exif
		;;
	esac  # is ridiculous ;-)
}

if [ $EUID != 0 ]
then
	echo "Must be executed with superuser priviledges."
	exit 1
fi

os=`uname`

case $os in
	"Linux")
		linux_dependencies
	;;
	*)
		echo "Unsupported operating system."
		echo "Try installing dependencies manually."
		exit 1
esac  # is ridiculous ;-)
