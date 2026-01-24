import sys
import os
from flask import Flask, request
from satellite import Satellite
from routing import get_direction, add_direction, node_to_sat, sat_to_node
from allocation import allocate
import json
import requests
import threading
import random
import time

app = Flask(__name__)
target = None 

responses = {}

def send_data(host, port, path, data):
  requests.post(f"http://{host}:{port}/{path}", json=data)

def sat2host(sat):
  port = 8080 + sat[0]
  target_orb = sat[1]
  host = f"orb{target_orb}"
  return host,port

class ISL:
  def __init__(self):
    pass
  def send(self,sat,payload): 
    payload["target"] = sat
    if target.get_id != sat:
      direction = get_direction(target.get_id(), sat)
      next_sat = add_direction(target.get_id(),direction)
      action = payload["action"]
      print(f"DEBUG: ISL from {target.get_id()} to {sat} direction {direction} next {next_sat} action {action}") 
    else:
      next_sat = sat
    host,port = sat2host(next_sat)
    threading.Thread(target=send_data,args=(host,port,"send",payload)).start()

isl = ISL()

@app.route('/send', methods=['POST'])
def send():
  data = request.get_json(force=True)
  direction = None
  next_sat = None
  if data["target"] == target.get_id():
    result = target.dispatch(data)
    if "messageid" in data and data["messageid"] != 0 and not result is None:
      responses[data["messageid"]] = {"result": result, "payload":data}
  else:
    direction = get_direction(target.get_id(), data["target"])
    next_sat = add_direction(target.get_id(),direction)
    host,port = sat2host(next_sat)
    if not "route" in data:
      data["route"] = []
    data["route"].append(target.get_id())
    sat =  data["target"]
    action = data["action"]
    map_log = ""
    if "mapper" in data:
      map_log = "Mapper %s" % data["mapper"]
    print(f"DEBUG: Route {map_log} from {target.get_id()} to {sat} direction {direction} next {next_sat} action {action}") 
    threading.Thread(target=send_data,args=(host,port,"send",data)).start()

  output = {"status":"OK","direction": direction, "next_sat": next_sat}
  if "messageid" in data:
    output["messageid"] = data["messageid"]
  return json.dumps(output)


@app.route('/response', methods=['POST'])
def response():
  data = request.get_json(force=True)
  mid = data["messageid"]
  if mid in responses:
    result = responses[mid]
    del responses[mid]
    return json.dumps({"status":"OK","result": result})
  return json.dumps({"error":"NOT_FOUND"})
  
@app.route('/submit', methods=['POST'])
def submit():
  data = request.get_json(force=True)
  collectors = data["collectors"]
  aoi_sats = data["aoi"]

  random.shuffle(aoi_sats)
  sat_tasks = aoi_sats[:collectors]
  sat_processors = aoi_sats[collectors:collectors*2]

  # initiate collect phase on task nodes
  #for sat_task in sat_tasks:
  #  data = {"messagid":0,"action":"collect","target": sat_task}
  #  host,port = sat2host(sat_task)
  #  threading.Thread(target=send_data,args=(host,port,"send",data)).start()
  #print(f"DEBUG: Sat Tasks {sat_tasks} Processors {sat_processors}")
  allocator = data["allocator"]
  allocations = allocate(sat_tasks, sat_processors,allocator)

  target.set_expected_map_count(len(allocations))
  # allocate map tasks
  i = 0
  job_start = time.time()
  for allocation in allocations:
    i += 1
    task = allocation[0]
    processor = allocation[1]
    data = {"meta_data": {
                 "collect_task": "doccollector",
                 "data_id": i,
                 "job_start": job_start,
                 "filename": "data/sample.txt",
                 "map_task": "wordcountmapper",
                 "reduce_task":"sumreducer"
            },
            "reducer": target.get_id(),"action":"map","target": processor, "collector": task}
    print(f"DEBUG: Submitting allocation {allocation} Map Task {data}")
    host,port = sat2host(processor)
    threading.Thread(target=send_data,args=(host,port,"send",data)).start()

  return json.dumps({"allocations":allocations,"allocator": allocator})
 
@app.route('/completion', methods=['POST'])
def completion():
    result = {"done": target.is_reduce_done()}
    if target.is_reduce_done():
      result["result"] = target.reduce_result
      result["job_time"] = target.job_time
    return json.dumps(result)

if __name__ == '__main__':
    sat = int(sys.argv[1])
    orb = int(sys.argv[2])
    port = 8080 + sat
    target = Satellite(sat,orb,isl)
    app.run(host='0.0.0.0',debug=False, port=port)
