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

"""Controls Phil Harvey's ExifTool through a pipe to extract metadata."""

import os
import json
from subprocess import Popen, PIPE


class ExifTool:
    """Encapsulate a running ExifTool process to retrieve metadata."""

    COMMAND = [
        "exiftool",
        "-stay_open",
        "True",
        "-@",
        "-",
        "-common_args",
        "-G",
        "-n",
        "-b",
    ]
    STOP = ["-stay_open", "False"]

    def __init__(self):
        """Start running ExifTool in the background."""
        self._running = False
        self._process = None

    def start(self):
        """Initialize the Exiftool application."""
        with open(os.devnull, "w") as devnull:
            self._process = Popen(
                ExifTool.COMMAND, stdin=PIPE, stdout=PIPE, stderr=devnull
            )
            self._running = True

    def terminate(self):
        """Terminate the running process if it is still running."""
        if self._running:
            self._send_cmd(ExifTool.STOP)
            self._process.communicate()
            del self._process
            self._running = False

    def _read_response(self, mark):
        if not self._running:
            raise Exception("This should only be called from inside ExifTool.")
        output = b""
        rd = b""
        lsz = -len(mark)
        fd = self._process.stdout.fileno()
        while not rd[2 * lsz :].strip().endswith(mark):
            rd = os.read(fd, 4096)
            output += rd
        return output.strip()[:lsz]

    def _execute(self, *files):
        if not self._running:
            raise Exception("ExifTool must be running. Use 'start()' before.")
        params = [*files, "-execute"]
        self._send_cmd(params)
        return self._read_response(b"{ready}")

    def get_metadata(self, *files):
        """Retrieve metadata in JSON format."""
        if not self._running:
            raise Exception("ExifTool must be running. Use 'start()' before.")
        return json.loads(self._execute("-j", *files).decode("utf-8"))

    def get_image_preview(self, *files):
        """Retrieve preview images in base64."""
        return self._execute("-PreviewImage", *files)

    def _send_cmd(self, *args):
        """Send a command to the running process."""
        if self._running:
            params = [i for subl in args for i in subl]
            data = "%s\n" % "\n".join(params)
            self._process.stdin.write(bytes(data.encode("utf-8")))
            self._process.stdin.flush()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Terminate program when object does not exist anymore."""
        self.terminate()

    def __del__(self):
        """Terminate program when object does not exist anymore."""
        self.terminate()

    def __enter__(self):
        """Start context."""
        self.start()
        return self
