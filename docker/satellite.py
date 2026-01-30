# /usr/bin/env python3
import routing
import hungarian
from config import config
from comp import comp_finder
import time

class Satellite:
  def __init__(self, sat, orb, isl, jobid):
    self.sat = sat
    self.orb = orb
    self.isl = isl
    self.map_count = 0
    self.expected_map_count = -1
    self.data = None
    self.reduced_data = []
    self.reduce_result = {}
    self.reduce_done = False
    self.remote_reducer = None
    self.jobid = jobid
  def dispatch(self,payload):
    action = payload["action"]
    print(f"DEBUG: Dispatching {action} on {self.get_id()}")
    if action == "collect":
      return self.collect(payload)
    if action == "map":
      return self.start_map(payload)
    if action == "collect_data":
      return self.collect_data(payload)
    if action == "reduce_data":
      return self.reduce_data(payload)
    if action == "get_reduce_result":
      return self.get_reduce_result(payload)
    if action == "reduce_response":
      return self.reduce_response(payload)
    if action == "set_map_count":
      print(f"DEBUG: Setting expected map count {self.expected_map_count} in sat {self.get_id()}")
      self.expected_map_count = payload["data"]["map_count"]
      return
    return {"error":"Unkown action"}
  def start_map(self,payload):
    self.reducer = payload["reducer"]
    self.isl.send(payload["collector"],{"meta_data": payload["meta_data"], "action":"collect","mapper": self.get_id()})
  def collect(self,payload):
    collect_task = comp_finder.find_collect(payload["meta_data"]["collect_task"])
    data = collect_task.collect(payload)
    self.isl.send(payload["mapper"],{"meta_data": payload["meta_data"],"action":"collect_data","last": True, "data": data, "collector": self.get_id()})
  def collect_data(self,payload):
    map_task = comp_finder.find_map(payload["meta_data"]["map_task"])
    mapped_data = map_task.run_map(payload)
    print(f"DEBUG: Sending Data from Mapper {self.get_id()} to Reducer {self.reducer}")
    self.isl.send(self.reducer,{"meta_data": payload["meta_data"], "action":"reduce_data","data": mapped_data, "mapper": self.get_id()})
  def reduce_data(self,payload):
    self.map_count += 1
    mapper = payload["mapper"]
    print(f"DEBUG: Got Data from Mapper {mapper} count {self.map_count} in sat {self.get_id()}")
    self.reduced_data.append(payload)
    if self.is_map_done():
      reduce_task = comp_finder.find_reduce(payload["meta_data"]["reduce_task"])
      self.reduce_result = reduce_task.reduce(self.reduced_data)
      self.reduce_done = True
      self.job_time = time.time() - payload["meta_data"]["job_start"]
  def get_reduce_result(self,payload):
    los = payload["los"]
    result = {"done": self.is_reduce_done()}
    if self.is_reduce_done():
        result["result"] = self.reduce_result
        result["job_time"] = self.job_time
    self.isl.send(los,{"meta_data": payload["meta_data"], "action":"reduce_response","data": result, "reducer": self.get_id()})
  def reduce_response(self,payload):
      self.reduce_done = payload["data"]["done"]
      if payload["data"]["done"]:
          self.reduce_result = payload["data"]["result"]
          self.job_time = payload["data"]["job_time"]
  def set_expected_map_count(self, expected_count):
     if not self.remote_reducer is None:
       self.isl.send(self.remote_reducer,{"meta_data": {"jobid":self.jobid}, "action":"set_map_count","data": {"map_count":expected_count}})
     else:
       print(f"DEBUG: Setting expected map count {self.expected_map_count} in sat {self.get_id()}")
       self.expected_map_count = expected_count
  def is_map_done(self):
     return self.expected_map_count == self.map_count
  def is_reduce_done(self):
    return self.reduce_done
  def get_id(self):
    return [self.sat,self.orb]
