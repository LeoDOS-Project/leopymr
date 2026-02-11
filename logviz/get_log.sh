#! /bin/bash
cd ../
./logs.sh $1 | python3 logviz/logparse.py > logviz/${1}.jsonl

