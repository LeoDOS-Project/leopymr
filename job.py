#! /usr/bin/env python3

import requests
import json
import sys
import random
import argparse
import time


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
        '-f',
        '--file',
        default=None,
        help="can be used with job id to download a job result file",
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
        '-cbt',
        '--combinetask',
        default='mergecombiner',
        help="combiner task",
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
  parser.add_argument(
        '-u',
        '--url',
        default="http://localhost:8089",
        help="gateway server endpoint",
        type=str)


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
        "combine_task": args.combinetask,
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

  json_result = True

  if args.id is None:
    res = requests.post(f"{args.url}/submit", json=data)
  else:
    data = {"jobid": args.id}
    if args.file is None:
      res = requests.post(f"{args.url}/completion", json=data)
      if not res.json()["done"]:
        time.sleep(0.5)
        res = requests.post(f"{args.url}/completion", json=data)
    else:
      json_result = False
      data["file"] = args.file
      res = requests.post(f"{args.url}/download", json=data)
      if res.status_code == 200:
        with open(args.file,'wb') as f:
          f.write(res.content)
          print(f"Downloaded {args.file}")
      else:
        print(f"Failed to download {args.file}")
        print(f"Status: {res.status_code}")

  
  if json_result:
    print(json.dumps(res.json()))
