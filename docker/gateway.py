import sys
import os
from flask import Flask, request, send_file, abort, Response
from routing import get_direction, add_direction, node_to_sat, sat_to_node
from allocation import allocate
import json
import requests
import threading
import random
import time
import io
import queue

app = Flask(__name__)

class PubSub:
  def __init__(self):
    self.listeners = []
  def subscribe(self):
    self.listeners.append(queue.Queue(maxsize=15))
    return self.listeners[-1]
  def publish(self, msg):
    for i in reversed(range(len(self.listeners))):
      try:
        self.listeners[i].put_nowait(msg)
      except queue.Full:
        del self.listeners[i]

pubsub = PubSub()


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
  try:
    res = send_data(host,port,"submit",data)
    result = res.json()
  except Exception as inst:
      result = {"error": f"{inst}"}
  return json.dumps(result)
 
@app.route('/completion', methods=['POST'])
def completion():
  data = request.get_json(force=True)
  host,port = sat2host([1,1])
  try:
    res = send_data(host,port,"completion",data)
    result = res.json()
  except Exception as inst:
    result = {"error": f"{inst}"}
  return json.dumps(result)

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

@app.route('/publish', methods=['POST'])
def broadcast():
    data = request.get_json(force=True)
    msg = f'data: {json.dumps(data)}\n\n'
    msg = f'event: spacecomp\n{msg}'
    pubsub.publish(msg)
    return json.dumps({"status":"OK"})

@app.route('/subscribe', methods=['GET'])
def subscribe():
  def stream():
    messages = pubsub.subscribe()
    while True:
      msg = messages.get()
      yield msg
  return Response(stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False, port=8089)
