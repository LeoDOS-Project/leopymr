#! /bin/bash
SAT=$1
ORB=$2
MID=$RANDOM
docker exec -it leopymr-orb1-1 curl -d '{"action":"echo","messageid":"'${MID}'","target":['${SAT}','${ORB}']}' http://orb1:8081/send
