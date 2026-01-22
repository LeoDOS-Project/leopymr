#! /bin/bash
SAT=$1
ORB=$2
MID=$3
PORT=`echo "${SAT}+8080" | bc`
docker exec -it leopymr-orb${ORB}-1 curl -d '{"messageid":"'${MID}'"}' http://orb${ORB}:${PORT}/response
