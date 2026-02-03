#! /usr/bin/env python3

import os
import math

class DocCollector:
  def __init__(self):
    pass
  def collect(self,payload):
    data = []
    data_id = payload["meta_data"]["data_id"]
    data_size = payload["meta_data"]["data_size"]
    filename = payload["meta_data"]["job_data"]["filename"]
    file_size = os.path.getsize(filename)
    chunk_size = math.ceil(file_size/data_size)
    from_chunk = chunk_size * (data_id-1)
    print(f"DEBUG doccollect file size {file_size} chunk size {chunk_size} from chunk {from_chunk}")
    with open(filename) as f:
      f.seek(from_chunk)
      data = f.read(chunk_size).split("\n")
    return data

def get_task():
  return DocCollector()



