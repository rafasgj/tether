#!/bin/sh

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

linux_dependencies() {
	# shellcheck disable=SC1091
	. /etc/os-release
 	case $NAME in
		"Fedora")
			gphoto="libgphoto2 libgphoto2-devel python3-devel"
			gtk="cairo-devel cairo-gobject-devel"
			gobject="gobject-introspection-devel"
			exif="perl-Image-ExifTool"
			# shellcheck disable=SC2086
			dnf install $gphoto $gtk $exif $gobject
		;;
		*)
			echo "Distribution not supported."
			exit 1
		;;
	esac  # is ridiculous ;-)
}

if [ "$(id -u)" != 0 ]
then
	echo "Must be executed with superuser priviledges."
	exit 1
fi

os=$(uname)

case $os in
	"Linux")
		linux_dependencies
	;;
	*)
		echo "Unsupported operating system."
		echo "Try installing dependencies manually."
		exit 1
esac  # is ridiculous ;-)
