#! /bin/bash
BENCHES="random bipartite"
echo "BENCH VAL ITER" > result.dat
for ITER in `seq 1 10`; do
SEED=$RANDOM
for BENCH in $BENCHES; do
  ./up.sh test
  sleep 15
  python3 submit.py $BENCH $SEED los
  sleep 15
  VAL=`./job_time.sh`
  echo "$BENCH $VAL $ITER" >> result.dat
done
done
