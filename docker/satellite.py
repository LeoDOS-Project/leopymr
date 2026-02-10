# /usr/bin/env python3
import routing
import hungarian
from config import config
from comp import comp_finder
from utils import log
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
    self.total_mapped = 0
    self.reduce_files = None
  def dispatch(self,payload, files):
    if len(files) > 0:
      payload["files"] = files
    payload["target_sat"] = self
    action = payload["action"]
    log(f"Dispatching",sat=self,context=payload)
    if action == "collect":
      self.collect(payload)
    elif action == "map":
      self.start_map(payload)
    elif action == "collect_data":
      self.collect_data(payload)
    elif action == "reduce_data":
      self.reduce_data(payload)
    elif action == "get_reduce_result":
      self.get_reduce_result(payload)
    elif action == "reduce_response":
      self.reduce_response(payload)
    elif action == "set_map_count":
      self.expected_map_count = payload["data"]["map_count"]
      log(f"Setting expected map count {self.expected_map_count}",sat=self,context=payload)
    else:
      log(f"Unknown action",sat=self,context=payload,verbosity=0)
  def start_map(self,payload):
    self.reducer = payload["reducer"]
    self.isl.send(payload["collector"],{"meta_data": payload["meta_data"], "action":"collect","mapper": self.get_id()})
  def collect(self,payload):
    collect_task = comp_finder.find_collect(payload["meta_data"]["collect_task"])
    total_collected = 0
    data = []
    files = {}
    for record in collect_task.collect(payload):
      total_collected += 1
      if isinstance(record, dict) and "_COMP_FILE_" in record:
        files[record["_COMP_FILE_"]["name"]] = record["_COMP_FILE_"]["stream"]
        data.append(record["value"])  
      else:
        data.append(record)
      if len(data) >= payload["meta_data"]["max_collect_records"]:
        self.isl.send(payload["mapper"],{"meta_data": payload["meta_data"],"action":"collect_data", "end_collect": False, "collected_index": total_collected,"data": data, "collector": self.get_id()},files)
        data = []
        files = {}
    self.isl.send(payload["mapper"],{"meta_data": payload["meta_data"],"action":"collect_data", "collected_index": total_collected, "end_collect": True, "data": data, "collector": self.get_id()},files)
  def collect_data(self,payload):
    map_task = comp_finder.find_map(payload["meta_data"]["map_task"])
    if payload["end_collect"] and "data" in payload and len(payload["data"]) == 0:
      self.isl.send(self.reducer,{"mapped_index": self.total_mapped, "meta_data": payload["meta_data"], "action":"reduce_data","end_map": True, "mapper": self.get_id()})
      return
    for mapped_data in map_task.run_map(payload):
      self.total_mapped += 1
      if isinstance(mapped_data, dict) and "_COMP_FILE_" in mapped_data:
        files = {}
        files[mapped_data["_COMP_FILE_"]["name"]] = mapped_data["_COMP_FILE_"]["stream"]
        self.isl.send(self.reducer,{"mapped_index": self.total_mapped, "meta_data": payload["meta_data"], "action":"reduce_data","end_map": payload["end_collect"], "data": mapped_data["value"], "mapper": self.get_id()},files)
      else:
        self.isl.send(self.reducer,{"mapped_index": self.total_mapped, "meta_data": payload["meta_data"], "action":"reduce_data","end_map": payload["end_collect"], "data": mapped_data, "mapper": self.get_id()})
  def reduce_data(self,payload):
    if payload["end_map"]:
      self.map_count += 1
    mapper = payload["mapper"]
    log(f"Got Data from Mapper {mapper} count {self.map_count}",sat=self,context=payload)
    if "data" in payload:
      self.reduced_data.append(payload)
    if self.is_map_done():
      reduce_task = comp_finder.find_reduce(payload["meta_data"]["reduce_task"])
      self.reduce_result = reduce_task.reduce(self.reduced_data)
      if isinstance(self.reduce_result, dict) and "_COMP_FILE_" in self.reduce_result:
        files = {}
        files[self.reduce_result["_COMP_FILE_"]["name"]] = self.reduce_result["_COMP_FILE_"]["stream"]
        self.reduce_files = files
      self.reduce_done = True
      self.job_time = time.time() - payload["meta_data"]["job_start"]
  def get_reduce_result(self,payload):
    los = payload["los"]
    result = {"done": self.is_reduce_done()}
    files = {}
    if self.is_reduce_done():
        if isinstance(self.reduce_result, dict) and "_COMP_FILE_" in self.reduce_result:
          files[self.reduce_result["_COMP_FILE_"]["name"]] = self.reduce_result["_COMP_FILE_"]["stream"]
          result["result"] = self.reduce_result["_COMP_FILE_"]["name"]
        else:
          result["result"] = self.reduce_result
        result["job_time"] = self.job_time
    self.isl.send(los,{"meta_data": payload["meta_data"], "action":"reduce_response","data": result, "reducer": self.get_id()},files)
  def reduce_response(self,payload):
      self.reduce_done = payload["data"]["done"]
      if payload["data"]["done"]:
          self.reduce_result = payload["data"]["result"]
          if "files" in payload:
            self.reduce_files = payload["files"]
          self.job_time = payload["data"]["job_time"]
  def set_expected_map_count(self, expected_count):
     if not self.remote_reducer is None:
       self.isl.send(self.remote_reducer,{"meta_data": {"jobid":self.jobid}, "action":"set_map_count","data": {"map_count":expected_count}})
     else:
       self.expected_map_count = expected_count
       log(f"Setting expected map count {self.expected_map_count}",sat=self)
  def is_map_done(self):
     return self.expected_map_count == self.map_count
  def is_reduce_done(self):
    return self.reduce_done
  def get_id(self):
    return [self.sat,self.orb]
