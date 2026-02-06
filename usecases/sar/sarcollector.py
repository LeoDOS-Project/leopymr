#! /usr/bin/env python3

import glob,os
import math
from deepdespeckling.despeckling import despeckle
from deepdespeckling.utils import utils
import numpy

import torch.serialization

torch.serialization.add_safe_globals([numpy.core.multiarray.scalar,
                                      numpy.dtype,
                                      numpy.dtypes.Float64DType])

class SarCollector:
  def __init__(self):
    pass
  def collect(self,payload):
    data_id = payload["meta_data"]["data_id"]
    image_path=f"data/task{data_id}"
    destination_directory=f"data/output{data_id}"
    despeckle(image_path, destination_directory, model_name="sar2sar")

    for file in glob.glob(f"data/task{data_id}/*.tiff"):
      fname = file.split('/')[-1].split('.tiff')[0]
      file_path = f"data/output{data_id}/denoised/denoised_{fname}.png"
      yield {"value": fname + ".png", "file": {"name": fname + ".png", "stream": open(file_path,'rb')}}

def get_task():
  return SarCollector()



