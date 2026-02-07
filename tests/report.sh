#! /bin/bash
FILTER="$*"
cat test_result.dat | grep "$FILTER"| awk '{SUM1+=$3;SUM2+=$4;SUM3+=$5} END {print SUM1/NR,SUM2/NR,SUM3/NR}'
