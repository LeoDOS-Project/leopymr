#! /bin/bash
COLLECTORS=$1
AOI="$2"
docker exec -it leopymr-orb1-1 curl -d '{"collectors":'${COLLECTORS}',"aoi":'${AOI}'}' http://orb1:8081/submit
