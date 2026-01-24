#! /bin/bash
COLLECTORS=$1
AOI="$2"
ALLOCATOR=${ALLOCATOR:-bipartite}
docker exec -it leopymr-orb1-1 curl -d '{"collectors":'${COLLECTORS}',"aoi":'${AOI}',"allocator":"'${ALLOCATOR}'"}' http://orb1:8081/submit
