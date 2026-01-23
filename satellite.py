# /usr/bin/env python3
import routing
import hungarian
from config import config

class Satellite:
  def __init__(self, sat, orb, isl):
    self.sat = sat
    self.orb = orb
    self.isl = isl
    self.map_count = 0
    self.expected_map_count = -1
    self.data = None
    self.reduced_data = []
    self.reduce_result = {}
    self.reduce_done = False

  def dispatch(self,payload):
    action = payload["action"]
    if action == "echo":
      return self.echo(payload)
    if action == "collect":
      return self.collect(payload)
    if action == "map":
      return self.run_map(payload)
    if action == "request_collector_data":
      return self.run_request_collector_data(payload)
    if action == "request_collector_data_response":
      return self.run_request_collector_data_response(payload)
    if action == "request_map_data":
      return self.run_request_map_data(payload)
    if action == "request_map_data_response":
      return self.run_request_map_data_response(payload)
    if action == "get_reduce_result":
      return self.get_reduce_result(payload)
    return {"error":"Unkown action"}
  def echo(self,payload):
    return {"me":(self.sat,self.orb),"incoming": payload}
  def collect(self,payload):
    if self.data is None:
      self.data = [ self.orb, 1 ]
    self.data[1] += 1
    return None
  def run_map(self,payload):
    self.reducer = payload["reducer"]
    self.isl.send(payload["collector"],{"action":"request_collector_data","mapper": self.get_id()})
  def run_request_collector_data(self,payload):
      self.isl.send(payload["mapper"],{"action":"request_collector_data_response","last": True, "data": self.data, "collector": self.get_id()})
  def run_request_collector_data_response(self,payload):
    self.mapped_data = payload["data"]
    if payload["last"]:
      print(f"DEBUG: Sending Data from Mapper {self.get_id()} to Reducer {self.reducer}")
      self.isl.send(self.reducer,{"action":"request_map_data_response","last": True, "data": self.mapped_data, "mapper": self.get_id()})
  def run_request_map_data(self,payload):
      self.isl.send(payload["reducer"],{"action":"request_map_data_response","last": True, "data": self.mapped_data, "mapper": self.get_id()})
  def run_request_map_data_response(self,payload):
    if payload["last"]:
      self.map_count += 1
    mapper = payload["mapper"]
    print(f"DEBUG: Got Data from Mapper {mapper} count {self.map_count} in sat {self.get_id()}")
    self.reduced_data.append(payload["data"])
    if self.is_map_done():
      self.reduce()
  def get_reduce_result(self,payload):
    return self.reduce_result
  def set_expected_map_count(self, expected_count):
     self.expected_map_count = expected_count
     print(f"DEBUG: Setting expected map count {self.expected_map_count} in sat {self.get_id()}")

  def is_map_done(self):
     return self.expected_map_count == self.map_count

  def reduce(self):
    if not self.is_map_done():
      return None
    self.reduce_result = {}
    for d in self.reduced_data:
      if d[0] not in self.reduce_result:
        self.reduce_result[d[0]] = 0
      self.reduce_result[d[0]] += d[1]
    self.reduce_done = True

  def is_reduce_done(self):
    return self.reduce_done

  def get_id(self):
    return [self.sat,self.orb]
