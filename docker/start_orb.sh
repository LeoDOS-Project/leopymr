#! /bin/bash
for i in `seq 1 ${MAX_SAT}`; do
  touch sat${ORB}.${i}.log 
  screen -d -m -S sat${ORB}.${i} -L -Logfile sat${ORB}.${i}.log python3 server.py $i $ORB	
done
tail -F *.log
