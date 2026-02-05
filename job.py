#! /usr/bin/env python3

import requests
import json
import sys
import random
import argparse
import time

SERVER = "http://localhost:8089/submit"


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        prog='job.py',
        description='Submits and gets results from collect mapreduce task')

  parser.add_argument(
        '-i',
        '--id',
        default=None,
        help="job id (specify to return results of job)",
        type=str)
  
  parser.add_argument(
        '-a',
        '--allocator',
        default="bipartite",
        help="map allocator",
        choices=['bipartite','random'])
  parser.add_argument(
        '-s',
        '--seed',
        default=-1,
        help="random aoi shuffle seed",
        type=int)
  parser.add_argument(
        '-r',
        '--reducetype',
        default="center",
        help="reduce placement",
        choices=['los','center'])

  parser.add_argument(
        '-mi',
        '--minsat',
        default=3,
        help="min aoi grid index",
        type=int)
  parser.add_argument(
        '-ma',
        '--maxsat',
        default=8,
        help="max aoi grid index",
        type=int)
  parser.add_argument(
        '-c',
        '--collectors',
        default=11,
        help="total collectors (and mappers)",
        type=int)
  parser.add_argument(
        '-ct',
        '--collecttask',
        default='doccollector',
        help="collector task",
        type=str)
  parser.add_argument(
        '-mt',
        '--maptask',
        default='wordcountmapper',
        help="mapper task",
        type=str)
  parser.add_argument(
        '-rt',
        '--reducetask',
        default='sumreducer',
        help="reducer task",
        type=str)
  parser.add_argument(
        '-d',
        '--data',
        default=None,
        help="job data file (json)",
        type=str)
  parser.add_argument(
        '-mr',
        '--maxrecords',
        default=1024,
        help="max records to collect before streaming to mapper",
        type=int)


  args = parser.parse_args()

  allocator = args.allocator
  seed = args.seed
  reduce_type = args.reducetype
  if seed != -1:
    random.seed(seed)

  minsat = args.minsat
  maxsat = args.maxsat

  aoi = []
  for sat in range(minsat,maxsat+1):
    for orb in range(minsat,maxsat+1):
      aoi.append([sat,orb])

  random.shuffle(aoi)
  collectors = args.collectors
  s=0
  o=0
  for c in range(collectors,collectors*2):
    s += aoi[c][0]
    o += aoi[c][1]

  center = [int(s/collectors),int(o/collectors)]
  data = {
        "collectors":collectors,
        "aoi":aoi,
        "allocator": allocator,
        "collect_task": args.collecttask,
        "map_task": args.maptask,
        "reduce_task": args.reducetask,
        "max_collect_records": args.maxrecords,
        }
  if args.data is None:
    data["job_data"] = {"filename": "data/sample.txt"}
  else:
    with open(args.data) as f:
      data["job_data"] = json.loads(f.read())

  if reduce_type == "center":
    data["reducer"] = center
  else:
    data["reducer"] = [1,1]

  if args.id is None:
    res = requests.post(f"http://localhost:8089/submit", json=data)
  else:
    data = {"jobid": args.id}
    res = requests.post(f"http://localhost:8089/completion", json=data)
    if not res.json()["done"]:
      time.sleep(0.5)
      res = requests.post(f"http://localhost:8089/completion", json=data)

  
  print(json.dumps(res.json()))
