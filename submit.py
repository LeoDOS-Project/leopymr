#! /usr/bin/env python3

import requests
import json
import sys
import random

SERVER = "http://localhost:8089/submit"
allocator = sys.argv[1]
seed = int(sys.argv[2])
random.seed(seed)

aoi = []
for sat in range(2,18):
  for orb in range(2,18):
    aoi.append([sat,orb])

random.shuffle(aoi)

data = {
        "collectors":50,
        "aoi":aoi,
        "allocator":allocator
        }



res = requests.post(f"http://localhost:8089/submit", json=data)
print(res.json())
