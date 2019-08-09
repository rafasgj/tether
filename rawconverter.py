"""Raw converter test."""

import rawpy
from PIL import Image

__params = rawpy.Params(
    demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
    use_camera_wb=True,
    fbdd_noise_reduction=rawpy.FBDDNoiseReductionMode.Off,  # Light, Full
    output_color=rawpy.ColorSpace.sRGB,  # Adobe, ProPhoto, raw, Wide, XYZ
    output_bps=8,  # 16
    exp_shift=0.5,   # linear: 0.25 = -2 stops, 8 = +3 stops.
    user_sat=2000,
)


def image_from_raw(filename, params=__params):
    """Create a nem Image from a RAW file."""
    with rawpy.imread(filename) as raw:
        rgb = raw.postprocess(params)
        return Image.fromarray(rgb, 'RGB')


if __name__ == "__main__":
    import sys
    import os.path

    filename, ext = os.path.splitext(os.path.basename(sys.argv[1]))
    img = image_from_raw(sys.argv[1])
    img.save("{}.jpg".format(filename))
