#! /bin/bash
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${DIR}
NAME=$1
MAX_SAT=${MAX_SAT:-11}
MAX_ORB=${MAX_ORB:-11}
SAT_RT=${SAT_RT:-sat}
cat > compose${NAME}.yaml <<ANY
services:
  gateway:
    build:
      context: docker
      dockerfile: Dockerfile.gateway
    environment:
      MAX_ORB: "${MAX_ORB}"
      MAX_SAT: "${MAX_SAT}"
    ports:
      - "8089:8089"
ANY

cat > compose${NAME}-stack.yaml <<ANY
services:
  gateway:
    hostname: gateway
    image: ${REGISTRY}/leopymr-gateway
    deploy:
      placement:
        constraints:
          - node.labels.node1 == true
    environment:
      MAX_ORB: "${MAX_ORB}"
      MAX_SAT: "${MAX_SAT}"
    ports:
      - target: 8089
        published: 8089
        mode: host
ANY

for i in `seq 1 ${MAX_ORB}`; do
cat > orb.tmp <<ANY
  orb${i}:
    build:
      context: docker
      dockerfile: Dockerfile.${SAT_RT}
    environment:
      ORB: "${i}"
      MAX_ORB: "${MAX_ORB}"
      MAX_SAT: "${MAX_SAT}"
ANY
cat > orb-stack.tmp <<ANY
  orb${i}:
    hostname: orb${i} 
    image: ${REGISTRY}/leopymr-gateway
    deploy:
      placement:
        constraints:
          - node.labels.node${i} == true
    environment:
      ORB: "${i}"
      MAX_ORB: "${MAX_ORB}"
      MAX_SAT: "${MAX_SAT}"
ANY

cat orb.tmp >> compose${NAME}.yaml
cat orb-stack.tmp >> compose${NAME}-stack.yaml
done
rm -f orb.tmp
rm -f orb-stack.tmp
