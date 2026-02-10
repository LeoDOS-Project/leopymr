import sys
import os
from flask import Flask, request, send_file, abort
from routing import get_direction, add_direction, node_to_sat, sat_to_node
from allocation import allocate
import json
import requests
import threading
import random
import time
import io

app = Flask(__name__)


def send_data(host, port, path, data):
  return requests.post(f"http://{host}:{port}/{path}", json=data)

def sat2host(sat):
  port = 8080 + sat[0]
  target_orb = sat[1]
  host = f"orb{target_orb}"
  return host,port

@app.route('/send', methods=['POST'])
def send():
  data = request.get_json(force=True)
  host,port = sat2host([1,1])
  res = send_data(host,port,"send",data)
  return json.dumps(res.json())

@app.route('/response', methods=['POST'])
def response():
  data = request.get_json(force=True)
  host,port = sat2host([1,1])
  res = send_data(host,port,"response",data)
  return json.dumps(res.json())
  
@app.route('/submit', methods=['POST'])
def submit():
  data = request.get_json(force=True)
  host,port = sat2host([1,1])
  res = send_data(host,port,"submit",data)
  return json.dumps(res.json())
 
@app.route('/completion', methods=['POST'])
def completion():
  data = request.get_json(force=True)
  host,port = sat2host([1,1])
  res = send_data(host,port,"completion",data)
  return json.dumps(res.json())

@app.route('/download', methods=['POST'])
def download():
   data = request.get_json(force=True)
   host,port = sat2host([1,1])
   res = send_data(host,port,"download",data)
   if res.status_code != 200:
     abort(res.status_code)
   return send_file(
    io.BytesIO(res.content),
    mimetype=res.headers['content-type'],
    as_attachment=True,
    download_name=data["file"])

   return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False, port=8089)
