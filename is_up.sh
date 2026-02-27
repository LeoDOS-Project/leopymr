#! /bin/bash
RT=$1
ORBS=`cat compose${RT}.yaml  | grep MAX_ORB | uniq | awk '{print $2}' | sed 's/"//g'`
SATS=`cat compose${RT}.yaml  | grep MAX_SAT | uniq | awk '{print $2}' | sed 's/"//g'`
EXPECTED=`echo "$ORBS * $SATS + 1" | bc`
CURRENT=`./logs.sh $RT | grep "Press CTRL+C" | wc -l | awk '{print $1}'`
echo "Expected $EXPECTED Current $CURRENT"
if [ $EXPECTED -eq $CURRENT ]; then
  echo "Constellation is UP"
  exit 0
else
  echo "Constellation is DOWN"
  exit 1
fi
