import numpy as np
import rawpy


def dng2png(dng_path):
    # Read RAW file
    with rawpy.imread(dng_path) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            no_auto_bright=True,
            output_bps=16
        )

    # Convert to float [0,1]
    rgb = rgb.astype(np.float32)
    rgb /= rgb.max()

    # Convert to 8-bit
    rgb_8bit = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)

    return rgb_8bit
