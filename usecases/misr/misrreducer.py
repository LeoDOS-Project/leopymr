#! /usr/bin/env python3

from utils import log
import numpy
from misr import misr_merge
import io

import torch.serialization

torch.serialization.add_safe_globals([numpy.core.multiarray.scalar,
                                      numpy.dtype,
                                      numpy.dtypes.Float64DType])


class MisrReducer:
    def __init__(self):
        pass

    def reduce(self, payloads):
        merge_files = []
        fnames = []
        for payload in payloads:
            fname = payload["data"]
            fnames.append(fname)
            data_id = payload["meta_data"]["data_id"]
            log(f"sarmap loading {fname} idx {data_id}", context=payload)
            merge_files.append(payload["files"][fname])
        merged_image = misr_merge(merge_files)
        byte_arr = io.BytesIO()
        merged_image.save(byte_arr, format='PNG')
        byte_arr_val = byte_arr.getvalue()
        merged_stream = io.BytesIO(byte_arr_val)
        output_name = "reduce_merged.png"
        return {
            "value": output_name,
            "_COMP_FILE_": {
                "name": output_name,
                "stream": merged_stream}}


def get_task():
    return MisrReducer()
