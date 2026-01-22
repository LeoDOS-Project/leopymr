import sys
import os
from flask import Flask, request
from satellite import Satellite
from routing import get_direction, add_direction
import json
import requests
import threading

app = Flask(__name__)
target = None 

responses = {}

def send_data(host, port, path, data):
  requests.post(f"http://{host}:{port}/{path}", json=data)

@app.route('/send', methods=['POST'])
def send():
  data = request.get_json(force=True)
  direction = None
  next_sat = None
  if data["target"] == target.get_id():
    result = target.send(data)
    responses[data["messageid"]] = {"result": result, "payload":data}
  else:
    direction = get_direction(target.get_id(), data["target"])
    next_sat = add_direction(target.get_id(),direction)
    port = 8080 + next_sat[0]
    target_orb = next_sat[1]
    host = f"orb{target_orb}"
    if not "route" in data:
      data["route"] = []
    data["route"].append(target.get_id())
    threading.Thread(target=send_data,args=(host,port,"send",data)).start()
  
  return json.dumps({"messageid": data["messageid"],"status":"OK","direction": direction, "next_sat": next_sat})


@app.route('/response', methods=['POST'])
def response():
  data = request.get_json(force=True)
  mid = data["messageid"]
  if mid in responses:
    result = responses[mid]
    del responses[mid]
    return json.dumps({"status":"OK","result": result})
  return json.dumps({"error":"NOT_FOUND"})
  

if __name__ == '__main__':
    sat = int(sys.argv[1])
    orb = int(sys.argv[2])
    port = 8080 + sat
    target = Satellite(sat,orb)
    app.run(host='0.0.0.0',debug=False, port=port)
