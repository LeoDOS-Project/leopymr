#! /usr/bin/env python3

from routing import get_node_dist_hops, node_to_sat, sat_to_node
import numpy as np
import random
import math
from config import config
import os
from hungarian import hungarian

def node_cost(hops, dist, ignore_distance,distances):
    return hops

def bipartite_scheduler(tasks,nodes,ignore_distance):
    weights = []
    for t in tasks:
      costs = []
      for n in nodes:
        (distance,hops,distances,sats_passed) = get_node_dist_hops(t,n)
        cost = node_cost(hops,distance,ignore_distance,distances)
        costs.append(cost)
      weights.append(costs)
    assignment, total_cost = hungarian(weights)  
    picks = [ None for _ in range(0,len(nodes)) ]
    for i in range(0,len(assignment)):
      picks[int(assignment[i][1])] = int(assignment[i][0])
    return picks

def allocate(sat_tasks, sat_nodes):
  tasks = list(map(lambda x: sat_to_node(x),sat_tasks))
  nodes = list(map(lambda x: sat_to_node(x),sat_nodes))
  task_indexes = bipartite_scheduler(tasks,nodes,True)
  allocation = []
  n = 0
  for t in task_indexes:
    allocation.append([node_to_sat(tasks[task_indexes[t]]),node_to_sat(nodes[n])])
    n += 1
  return allocation
