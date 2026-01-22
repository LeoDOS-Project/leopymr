#! /bin/bash
NAME=$1
MAX_SAT=${MAX_SAT:-3}
MAX_ORB=${MAX_ORB:-2}
echo "services:" > compose${NAME}.yaml

for i in `seq 1 ${MAX_ORB}`; do
cat > orb.tmp <<ANY
  orb${i}:
    build:
      context: .
      dockerfile: Dockerfile.sat
    environment:
      ORB: "${i}"
      MAX_ORB: "${MAX_ORB}"
      MAX_SAT: "${MAX_SAT}"
ANY
cat orb.tmp >> compose${NAME}.yaml
done
rm -f orb.tmp
