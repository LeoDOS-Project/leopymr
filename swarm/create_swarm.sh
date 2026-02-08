#! /bin/bash
NAME=$1
myhost=`hostname -I | awk '{print $1}'`
docker swarm init --advertise-addr $myhost
MYREGISTRY="${myhost}:5000"
if [ "X${REGISTRY}" == "X" ]; then
  docker run -d -p 5000:5000 --name registry registry:2.7
  echo "add \"insecure-registries\":[\"${myhost}\"] to /etc/docker/daemon.json"
fi
REGISTRY="${REGISTRY:-$MYREGISTRY}"
REGISTRY="${REGISTRY}" ./publish.sh
echo "Press enter when all swarm nodes have been added"
read
./label.sh
REGISTRY="${REGISTRY}" ./deploy.sh $NAME
