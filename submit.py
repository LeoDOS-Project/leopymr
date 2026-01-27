#! /usr/bin/env python3

import requests
import json
import sys
import random

SERVER = "http://localhost:8089/submit"
allocator = sys.argv[1]
seed = int(sys.argv[2])
reduce_type = sys.argv[3]
random.seed(seed)

aoi = []
for sat in range(2,18):
  for orb in range(2,18):
    aoi.append([sat,orb])

random.shuffle(aoi)
collectors = 50
s=0
o=0
for c in range(collectors,collectors*2):
  s += aoi[c][0]
  o += aoi[c][1]

center = [int(s/collectors),int(o/collectors)]
print(center)
data = {
        "collectors":50,
        "aoi":aoi,
        "allocator":allocator
        }

if reduce_type == "center":
  data["reducer"] = center

res = requests.post(f"http://localhost:8089/submit", json=data)
print(res.json())
