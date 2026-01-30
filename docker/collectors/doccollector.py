#! /usr/bin/env python3

class DocCollector:
  def __init__(self):
    pass
  def collect(self,payload):
    data = []
    data_id = payload["meta_data"]["data_id"]
    with open(payload["meta_data"]["job_data"]["filename"]) as f:
      i = 1
      for line in f:
        if i % data_id == 0:
          data.append(line.strip('\n'))
    return data

def get_task():
  return DocCollector()



