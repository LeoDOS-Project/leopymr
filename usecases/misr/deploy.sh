#! /bin/bash
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${DIR}
for i in `seq 1 3`; do
  mkdir -p ../../docker/data/task${i}
done
curl https://storage.googleapis.com/hdrplusdata/20171106_subset/bursts/0006_20160722_115157_431/payload_N001.dng > ../../docker/data/task1/N001.dng
curl https://storage.googleapis.com/hdrplusdata/20171106_subset/bursts/0006_20160722_115157_431/payload_N002.dng > ../../docker/data/task1/N002.dng

curl https://storage.googleapis.com/hdrplusdata/20171106_subset/bursts/0006_20160722_115157_431/payload_N003.dng > ../../docker/data/task2/N003.dng
curl https://storage.googleapis.com/hdrplusdata/20171106_subset/bursts/0006_20160722_115157_431/payload_N004.dng > ../../docker/data/task2/N004.dng

curl https://storage.googleapis.com/hdrplusdata/20171106_subset/bursts/0006_20160722_115157_431/payload_N005.dng > ../../docker/data/task3/N005.dng
curl https://storage.googleapis.com/hdrplusdata/20171106_subset/bursts/0006_20160722_115157_431/payload_N006.dng > ../../docker/data/task3/N006.dng

cp misrcollector.py ../../docker/collectors/
cp misrmapper.py ../../docker/mappers/
cp dng2png.py ../../docker/
cp Dockerfile.misr ../../docker/
cp requirements.txt.misr ../../docker/
echo "Constellation example: MAX_SAT=5 MAX_ORB=5 SAT_RT=misr ./create_constellation.sh misr"
echo "Submit example: python3 job.py -mi 1 -ma 4 -c 3 -ct misrcollector -mt misrmapper -rt misrreducer -r los -mr 1"
