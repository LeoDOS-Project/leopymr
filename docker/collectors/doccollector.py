#! /usr/bin/env python3

import os
import math


class DocCollector:
  def __init__(self):
    self.delimiter = '\n'
  def collect(self,payload):
    data = []
    data_id = payload["meta_data"]["data_id"]
    data_size = payload["meta_data"]["data_size"]
    filename = payload["meta_data"]["job_data"]["filename"]
    file_size = os.path.getsize(filename)
    chunk_size = math.ceil(file_size/data_size)
    from_chunk = chunk_size * (data_id-1)
    print(f"DEBUG doccollect file size {file_size} chunk size {chunk_size} from chunk {from_chunk}")
    skip_first = from_chunk != 0
    bytes_read = 0
    record = ""
    with open(filename) as f:
      f.seek(from_chunk)
      ch = f.read(1)
      while len(ch) == 1:
        if ch == self.delimiter:
          if not skip_first:
            yield record  
          skip_first = False
          record = "" 
          if bytes_read >= chunk_size:
            print(f"DEBUG doccollect file size {file_size} chunk size {chunk_size} from chunk {from_chunk} DONE {bytes_read}")
            return
        else:
          record += ch
        bytes_read += 1
        ch = f.read(1)
    if len(record) > 0:
      yield record
    print(f"DEBUG doccollect file size {file_size} chunk size {chunk_size} from chunk {from_chunk} DONE {bytes_read} EOF")

def get_task():
  return DocCollector()



