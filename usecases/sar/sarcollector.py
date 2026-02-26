#! /usr/bin/env python3

from utils import log
import glob
import os
import math
from deepdespeckling.despeckling import despeckle
from deepdespeckling.utils import utils
import numpy
from deepdespeckling.utils.load_cosar import load_tiff_image
from deepdespeckling.utils.constants import PATCH_SIZE, STRIDE_SIZE
from deepdespeckling.sar2sar.sar2sar_denoiser import Sar2SarDenoiser
import io
from PIL import Image


import torch.serialization

torch.serialization.add_safe_globals([numpy.core.multiarray.scalar,
                                      numpy.dtype,
                                      numpy.dtypes.Float64DType])


class SarCollector:
    def __init__(self):
        pass

    def collect(self, payload):
        data_id = payload["meta_data"]["data_id"]

        for image_path in glob.glob(f"data/task{data_id}/*.tiff"):
            denoiser = Sar2SarDenoiser()
            image = load_tiff_image(image_path).astype(numpy.float32)
            denoised_image = denoiser.denoise_image(
                image, patch_size=PATCH_SIZE, stride_size=STRIDE_SIZE)
            denoised_image = denoised_image["denoised"]

            byte_arr = io.BytesIO()
            denoised_image = Image.fromarray(
                denoised_image.astype('float64')).convert('L')
            denoised_image.save(byte_arr, format='PNG')
            byte_arr_val = byte_arr.getvalue()
            stream = io.BytesIO(byte_arr_val)
            fname = image_path.split('/')[-1].split('.tiff')[0]
            output_name = fname + ".png"
            log(
                f"sarcollector collected image {output_name} len {
                    len(byte_arr_val)}",
                context=payload)
            yield {"value": output_name, "_COMP_FILE_": {"name": output_name, "stream": stream}}


def get_task():
    return SarCollector()
