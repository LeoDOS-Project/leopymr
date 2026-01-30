import sys
import os
from flask import Flask, request
from satellite import Satellite
from routing import get_direction, add_direction, node_to_sat, sat_to_node, get_dist_hops
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
  if 'action' in data and data['action'] == "collect_data":
    print("DEBUG: SEND_COLLECT_DATA")
  if 'action' in data and data['action'] == "reduce_data":
    print("DEBUG: SEND_REDUCE_DATA")
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
  sat_tasks = aoi_sats[:collectors]
  sat_processors = aoi_sats[collectors:collectors*2]
  reducer = data.get("reducer")

  allocator = data["allocator"]
  allocations = allocate(sat_tasks, sat_processors,allocator)
  if "collect_task" in data:
    collect_task = data["collect_task"]
  else:
    collect_task = "doccollector"
  if "map_task" in data:
    map_task = data["map_task"]
  else:
    map_task = data["wordcountmapper"]
  if "reduce_task" in data:
    reduce_task = data["reduce_task"]
  else:
    reduce_task = "sumreducer" 

  # allocate map tasks
  distance = 0
  reduce_distance = 0
  for allocation in allocations:
    task = allocation[0]
    processor = allocation[1]
    (_,hops,_,_) = get_dist_hops(task, processor)
    distance += hops
    (_,reduce_hops,_,_) = get_dist_hops(processor,tuple(reducer))
    reduce_distance += reduce_hops
  if reducer is None or reducer == target.get_id():
    print(f"DEBUG: LOS REDUCER {target.get_id()}")
    reducer = target.get_id()
  else:
    target.remote_reducer = reducer
  target.set_expected_map_count(len(allocations))

  time.sleep(5)
  job_start = time.time()
  i = 0
  for allocation in allocations:
    i += 1
    task = allocation[0]
    processor = allocation[1]
    data = {"meta_data": {
                 "collect_task": collect_task,
                 "data_id": i,
                 "job_start": job_start,
                 "filename": "data/sample.txt",
                 "map_task": map_task,
                 "reduce_task": reduce_task
            },
            "action":"map","target": processor, "collector": task}
    print(f"DEBUG: REDUCE HOPS from {processor} to {reducer}")
    data["reducer"] = reducer
    print(f"DEBUG: Submitting allocation {allocation} Map Task {data}")
    host,port = sat2host(processor)
    threading.Thread(target=send_data,args=(host,port,"send",data)).start()


  return json.dumps({"reducer": reducer,"los": target.get_id(), "allocations":allocations,"allocator": allocator, "distance": distance, "reduce_distance": reduce_distance})
 
@app.route('/completion', methods=['POST'])
def completion():
    if not target.remote_reducer is None:
      data = {"meta_data":{},"action":"get_reduce_result","los": target.get_id()}
      isl.send(target.remote_reducer,data)
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
