#! /bin/bash
BENCHES="random bipartite"
PLACEMENTS="los center"
echo "BENCH PLACEMENT DISTANCE REDUCEDISTANCE VAL ITER" > result.dat
for ITER in `seq 1 10`; do
SEED=$RANDOM
for BENCH in $BENCHES; do
  for PLACEMENT in $PLACEMENTS; do
  ../up.sh test
  sleep 20
  python3 ../job.py -a $BENCH -s $SEED -r ${PLACEMENT} > submit.json
  DIST=`cat submit.json | jq .distance`
  REDDIST=`cat submit.json | jq .reduce_distance`
  sleep 25
  ./completion.sh
  sleep 20
  VAL=`./job_time.sh`
  echo "$BENCH ${PLACEMENT} ${DIST} ${REDDIST} $VAL $ITER" >> result.dat
done
done
done
