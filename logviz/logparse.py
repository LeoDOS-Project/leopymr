#! /usr/bin/env python2
import sys
import json

for line in sys.stdin:
  if line.find("COMPDEBUG") == -1:
    continue
  logpart = line.split('COMPDEBUG')[1]
  timestamp = logpart[logpart.find("[")+1:logpart.find("]")]
  if logpart.find("action=") == -1:
    continue
  if logpart.find("msg=") == -1:
    continue
  actionpart = logpart.split("action=")[1]
  action = actionpart[:actionpart.find(")")]

  msgpart = logpart.split("msg=")[1]
  msg = msgpart[:msgpart.find(")")]


  if logpart.find("Route") != -1:
    frompart = logpart.split("from")[1]
    fromsat = frompart[frompart.find("[")+1:frompart.find("]")]
    fromsat = fromsat.split(",")
    fromsat[0] = int(fromsat[0])
    fromsat[1] = int(fromsat[1])

    topart = frompart.split("next (")[1]
    tosat = topart[topart.find("(")+1:topart.find(")")]
    tosat = tosat.split(",")
    tosat[0] = int(tosat[0])
    tosat[1] = int(tosat[1])
  elif logpart.find("Dispatching") != -1:
    frompart = logpart.split("(sat=")[1]
    fromsat = frompart[frompart.find("[")+1:frompart.find("]")]
    fromsat = fromsat.split(",")
    fromsat[0] = int(fromsat[0])
    fromsat[1] = int(fromsat[1])
    tosat = fromsat
  else:
    continue
  record = {"timestamp":float(timestamp), "from": fromsat, "to": tosat, "action":action, "msgid":msg}
  print(json.dumps(record))
  
  
