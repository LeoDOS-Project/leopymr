# /usr/bin/env python3
import routing
import hungarian
from config import config

class Satellite:
  def __init__(self, sat, orb, isl):
    self.sat = sat
    self.orb = orb
    self.isl = isl
    self.data = None

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
    if action == "get_reduced_data":
      return self.get_reduced_data(payload)
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
    self.isl.send(payload["mapper"],{"action":"request_collector_data_response","data": self.data, "collector": self.get_id()})
  def run_request_collector_data_response(self,payload):
    self.mapped_data = payload["data"]
  def run_request_map_data(self,payload):
    self.isl.send(payload["reducer"],{"action":"request_map_data_response","data": self.mapped_data, "mapper": self.get_id()})
  def run_request_map_data_response(self,payload):
    if self.reduced_data is None:
      self.reduced_data = []
    self.reduced_data.append(payload["data"])
  def get_reduced_data(self,payload):
    return self.reduced_data
    
  def get_id(self):
    return [self.sat,self.orb]
