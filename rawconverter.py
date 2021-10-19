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

"""Raw converter test."""

import rawpy
from PIL import Image

__params = rawpy.Params(
    demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
    use_camera_wb=True,
    fbdd_noise_reduction=rawpy.FBDDNoiseReductionMode.Off,  # Light, Full
    output_color=rawpy.ColorSpace.sRGB,  # Adobe, ProPhoto, raw, Wide, XYZ
    output_bps=8,  # 16
    exp_shift=0.5,  # linear: 0.25 = -2 stops, 8 = +3 stops.
    user_sat=2000,
)


def image_from_raw(filename, params=__params):
    """Create a nem Image from a RAW file."""
    with rawpy.imread(filename) as raw:
        rgb = raw.postprocess(params)
        return Image.fromarray(rgb, "RGB")


if __name__ == "__main__":
    import sys
    import os.path

    filename, ext = os.path.splitext(os.path.basename(sys.argv[1]))
    img = image_from_raw(sys.argv[1])
    img.save("{}.jpg".format(filename))
