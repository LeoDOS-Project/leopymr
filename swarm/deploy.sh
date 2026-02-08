#! /bin/bash
NAME=$1
myhost=`hostname -I | awk '{print $1}'`
MYREGISTRY="${myhost}:5000"
REGISTRY="${REGISTRY:-$MYREGISTRY}"
REGISTRY="${REGISTRY}" docker stack deploy -c ../compose${NAME}-stack.yaml ${NAME}
