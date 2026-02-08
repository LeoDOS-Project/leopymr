#! /usr/bin/env python3

from routing import get_node_dist_hops, node_to_sat, sat_to_node
import random
import math
from config import config
import os
from hungarian import hungarian
from utils import log

def bipartite_scheduler(tasks,nodes):
    weights = []
    for t in tasks:
      costs = []
      for n in nodes:
        (distance,hops,distances,sats_passed) = get_node_dist_hops(t,n)
        costs.append(hops)
      weights.append(costs)
    assignment, total_cost = hungarian(weights)  
    picks = [ None for _ in range(0,len(nodes)) ]
    for i in range(0,len(assignment)):
      picks[int(assignment[i][1])] = int(assignment[i][0])
    return picks

def random_scheduler(tasks,nodes):
    indexes = list(range(0,len(tasks)))
    random.shuffle(indexes)
    return indexes

def allocate(sat_tasks, sat_nodes, allocator):
  tasks = list(map(lambda x: sat_to_node(x),sat_tasks))
  nodes = list(map(lambda x: sat_to_node(x),sat_nodes))

  if allocator == "random":
    task_indexes = random_scheduler(tasks,nodes)
  elif allocator == "bipartite":
    task_indexes = bipartite_scheduler(tasks,nodes)

  log(f"{allocator} Mappings {task_indexes}",verbosity=3)
  allocation = []
  n = 0
  for t in task_indexes:
    allocation.append([node_to_sat(tasks[t]),node_to_sat(nodes[n])])
    n += 1
  return allocation
