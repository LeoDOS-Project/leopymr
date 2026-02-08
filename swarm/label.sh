#! /bin/bash
i=1
NODES=`docker node ls | sed 's/*//' | awk '{print $2}' |  grep -v HOSTNAME`
for NODE in $NODES; do
 docker node update --label-add orb${i}=true $NODE 
 i=`expr $i + 1`
done
