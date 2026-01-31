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
import uuid

app = Flask(__name__)

target_config = None
targets = {}

def get_target(jobid=None):
  if jobid is None:
    jobid = str(uuid.uuid4())
    targets[jobid] =  Satellite(target_config["sat"],target_config["orb"],target_config["isl"],jobid)
  if jobid not in targets: 
    targets[jobid] =  Satellite(target_config["sat"],target_config["orb"],target_config["isl"],jobid)
  return targets[jobid]

  
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
    target_id = target_config["id"]
    if target_id != sat:
      direction = get_direction(target_id, sat)
      next_sat = add_direction(target_id, direction)
      action = payload["action"]
      print(f"DEBUG: ISL from {target_id} to {sat} direction {direction} next {next_sat} action {action}") 
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
  if data["target"] == target_config["id"]:
    target = get_target(data["meta_data"]["jobid"])
    target.dispatch(data)
  else:
    target_id = target_config["id"]
    direction = get_direction(target_id, data["target"])
    next_sat = add_direction(target_id, direction)
    host,port = sat2host(next_sat)
    if not "route" in data:
      data["route"] = []
    data["route"].append(target_id)
    sat =  data["target"]
    action = data["action"]
    map_log = ""
    if "mapper" in data:
      map_log = "Mapper %s" % data["mapper"]
    print(f"DEBUG: Route {map_log} from {target_id} to {sat} direction {direction} next {next_sat} action {action}") 
    threading.Thread(target=send_data,args=(host,port,"send",data)).start()

  output = {"status":"OK","direction": direction, "next_sat": next_sat}
  if "messageid" in data:
    output["messageid"] = data["messageid"]
  return json.dumps(output)


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

  target = get_target()

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

  job_start = time.time()
  i = 0
  for allocation in allocations:
    i += 1
    task = allocation[0]
    processor = allocation[1]
    payload = {"meta_data": {
                 "collect_task": collect_task,
                 "data_id": i,
                 "job_start": job_start,
                 "jobid": target.jobid,
                 "map_task": map_task,
                 "reduce_task": reduce_task,
                 "job_data": data.get("job_data")
            },
            "action":"map","target": processor, "collector": task}
    print(f"DEBUG: REDUCE HOPS from {processor} to {reducer}")
    payload["reducer"] = reducer
    print(f"DEBUG: Submitting allocation {allocation} Map Task {data}")
    host,port = sat2host(processor)
    threading.Thread(target=send_data,args=(host,port,"send",payload)).start()


  return json.dumps({"reducer": reducer,"los": target.get_id(), "allocations":allocations,"allocator": allocator, "distance": distance, "reduce_distance": reduce_distance, "jobid": target.jobid})
 
@app.route('/completion', methods=['POST'])
def completion():
    data = request.get_json(force=True)
    target = get_target(data["jobid"])
    sent_request = False
    if not target.remote_reducer is None:
      payload = {"meta_data":{"jobid":data["jobid"]},"action":"get_reduce_result","los": target.get_id()}
      isl.send(target.remote_reducer,payload)
      sent_request = True
    result = {"done": target.is_reduce_done(), "jobid": data["jobid"], "sent_request": sent_request}
    if target.is_reduce_done():
      result["result"] = target.reduce_result
      result["job_time"] = target.job_time
    return json.dumps(result)

if __name__ == '__main__':
    sat = int(sys.argv[1])
    orb = int(sys.argv[2])
    port = 8080 + sat
    target_config = {"sat": sat,"orb":orb,"isl": isl, "id": [sat,orb]}
    app.run(host='0.0.0.0',debug=False, port=port)
