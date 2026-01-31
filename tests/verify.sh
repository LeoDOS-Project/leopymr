#! /bin/bash
compare_report () {
  # commands to execute
  VALS1=`./report.sh $1 $2`
  VALS2=`./report.sh $3 $4`
  V11=`echo "$VALS1" | awk '{print $1}'`
  V12=`echo "$VALS1" | awk '{print $2}'`
  V13=`echo "$VALS1" | awk '{print $3}'`
  V21=`echo "$VALS2" | awk '{print $1}'`
  V22=`echo "$VALS2" | awk '{print $2}'`
  V23=`echo "$VALS2" | awk '{print $3}'`
  R1=`echo "$V11 > $V21" | bc`
  R2=`echo "$V12 > $V22" | bc`
  R3=`echo "$V13 > $V23" | bc`
  echo "$R1 $R2 $R3"
}
RES=$(compare_report random "" bipartite "")
OK1=0
echo $RES | grep -q "1 . 1" && OK1=1
echo "1. RANDOM > BIPARTITE: $RES"

RES=$(compare_report los "" center "")
OK2=0
echo $RES | grep -q ". 1 ." && OK2=1
echo "2. LOS > CENTER: $RES"

RES=$(compare_report random los random center)
OK3=0
echo $RES | grep -q ". 1 ." && OK3=1
echo "3. RANDOM LOS > RANDOM CENTER: $RES"

RES=$(compare_report bipartite los bipartite center)
OK4=0
echo $RES | grep -q ". 1 1" && OK4=1
echo "4. BIPARTITE LOS > BIPARTITE CENTER: $RES"

RES=$(compare_report random los bipartite center)
OK5=0
echo $RES | grep -q "1 1 1" && OK5=1
echo "5. RANDOM LOS > BIPARTITE CENTER: $RES"

echo "TEST_REPORT 1:$OK1 2:$OK2 3:$OK3 4:$OK4 5:$OK5"

ALLOK=0
echo "$OK1 $OK2 $OK3 $OK4 $OK5" | grep -q "1 1 1 1 1" && ALLOK=1

if [ $ALLOK -eq 1 ]; then
  echo "ALL TESTS PASSED"
  exit 0
else
  echo "SOME TESTS FAILED"
  exit 1
fi
