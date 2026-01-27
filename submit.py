#! /usr/bin/env python3

import requests
import json
import sys
import random
import argparse

SERVER = "http://localhost:8089/submit"


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        prog='submit.py',
        description='Submits collect mapreduce task')

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
        default=2,
        help="min aoi grid index",
        type=int)
  parser.add_argument(
        '-ma',
        '--maxsat',
        default=18,
        help="max aoi grid index",
        type=int)
  parser.add_argument(
        '-c',
        '--collectors',
        default=50,
        help="total collectors (and mappers)",
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
  for sat in range(minsat,maxsat):
    for orb in range(minsat,maxsat):
      aoi.append([sat,orb])

  random.shuffle(aoi)
  collectors = args.collectors
  s=0
  o=0
  for c in range(collectors,collectors*2):
    s += aoi[c][0]
    o += aoi[c][1]

  center = [int(s/collectors),int(o/collectors)]
  print(center)
  data = {
        "collectors":collectors,
        "aoi":aoi,
        "allocator":allocator
        }

  if reduce_type == "center":
    data["reducer"] = center

  res = requests.post(f"http://localhost:8089/submit", json=data)
  print(res.json())
