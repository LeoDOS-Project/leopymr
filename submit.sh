#! /bin/bash
COLLECTORS=$1
AOI="$2"
ALLOCATOR=${ALLOCATOR:-bipartite}
curl -d '{"collectors":'${COLLECTORS}',"aoi":'${AOI}',"allocator":"'${ALLOCATOR}'"}' http://localhost:8089/submit
