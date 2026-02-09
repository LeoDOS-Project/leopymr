import sys
import numpy as np
import rawpy
import imageio.v2 as imageio


def dng2png(dng_path, png_path=None):
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

    if png_path is None:
        return rgb_8bit
    # Write PNG
    imageio.imwrite(png_path, rgb_8bit)
    print(f"Saved PNG to: {png_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python dng_to_png.py input.dng output.png")
        sys.exit(1)

    dng_path = sys.argv[1]
    png_path = sys.argv[2]

    dng2png(dng_path, png_path)

