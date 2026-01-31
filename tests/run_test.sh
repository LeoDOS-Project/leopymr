#! /bin/bash
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${DIR}
BENCHES="random bipartite"
PLACEMENTS="los center"
ITERATIONS=${ITERATIONS:-1}
echo "BENCH PLACEMENT DISTANCE REDUCEDISTANCE VAL ITER" > result.dat
MAX_SAT=11 MAX_ORB=11 ../create_constellation.sh test
for ITER in `seq 1 $ITERATIONS`; do
SEED=$RANDOM
for BENCH in $BENCHES; do
  for PLACEMENT in $PLACEMENTS; do
  ../up.sh test
  sleep 10
  python3 ../job.py -a $BENCH -s $SEED -r ${PLACEMENT} -mi 3 -ma 8 -c 15 > submit.json
  DIST=`cat submit.json | jq .distance`
  REDDIST=`cat submit.json | jq .reduce_distance`
  JOBID=`cat submit.json | jq -r .jobid`
  sleep 5
  python3 ../job.py -i $JOBID
  sleep 5
  VAL=`python3 ../job.py -i $JOBID | jq .job_time`
  echo "$BENCH ${PLACEMENT} ${DIST} ${REDDIST} $VAL $ITER" >> result.dat
done
done
done
./verify.sh
RETURN_CODE=$?
echo "VERIFICATION $RETURN_CODE"
exit ${RETURN_CODE}
