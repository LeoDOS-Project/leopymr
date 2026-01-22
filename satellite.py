# /usr/bin/env python3
import routing
import hungarian
from config import config

class Satellite:
  def __init__(self, sat, orb):
    self.sat = sat
    self.orb = orb
  def send(self,payload):
    action = payload["action"]
    if action == "echo":
      return self.echo()
    return {"error":"Unkown action"}
  def echo(self):
    return (self.sat,self.orb)
  def get_id(self):
    return [self.sat,self.orb]
