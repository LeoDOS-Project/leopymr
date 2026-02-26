#! /usr/bin/env python3

from utils import log
import glob
import os
import math
import numpy
import io
from PIL import Image

from dng2png import dng2png

import torch.serialization

torch.serialization.add_safe_globals([numpy.core.multiarray.scalar,
                                      numpy.dtype,
                                      numpy.dtypes.Float64DType])


class MisrCollector:
    def __init__(self):
        pass

    def collect(self, payload):
        data_id = payload["meta_data"]["data_id"]

        for image_path in glob.glob(f"data/task{data_id}/*.dng"):
            converted_image = dng2png(image_path)
            byte_arr = io.BytesIO()
            image = Image.fromarray(converted_image, mode="RGB")
            image.save(byte_arr, format='PNG')
            byte_arr_val = byte_arr.getvalue()
            stream = io.BytesIO(byte_arr_val)
            fname = image_path.split('/')[-1].split('.dng')[0]
            output_name = fname + ".png"
            log(
                f"misrcollector converted dng to png image {output_name} len {
                    len(byte_arr_val)}",
                context=payload)
            yield {"value": output_name, "_COMP_FILE_": {"name": output_name, "stream": stream}}


def get_task():
    return MisrCollector()
