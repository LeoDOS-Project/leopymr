#! /usr/bin/env python3

from utils import log
import glob,os
import math
from deepdespeckling.despeckling import despeckle
from deepdespeckling.utils import utils
import numpy
from misr import misr_merge

import torch.serialization

torch.serialization.add_safe_globals([numpy.core.multiarray.scalar,
                                      numpy.dtype,
                                      numpy.dtypes.Float64DType])

class MisrMapper:
  def __init__(self):
    self.delimiter = '\n'
  def run_map(self,payload):
    merge_files = []
    data_id = payload["meta_data"]["data_id"]
    for fname in payload["data"]:
      log(f"sarmap loading {fname} idx {data_id}",context=payload)
      merge_files.append( payload["files"][fname])
      if len(merge_files) > 1:
          merged_image = misr_merge(merge_files)
          byte_arr = io.BytesIO()
          merged_image.save(byte_arr, format='PNG')
          byte_arr_val = byte_arr.getvalue()
          merged_stream = io.BytesIO(byte_arr_val)
          merge_files = []
          log(f"misrmap merged {payload['data']} idx {data_id}",context=payload)
          output_name = f"task{data_id}.png"
          yield {"value": output_name, "file": {"name": output_name, "stream": merged_stream}}

def get_task():
  return MisrMapper()



