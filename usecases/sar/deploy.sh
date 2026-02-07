#! /bin/bash
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${DIR}
curl -s https://storage.googleapis.com/mediapipe-models/object_detector/ssd_mobilenet_v2/float32/latest/ssd_mobilenet_v2.tflite > ../../docker/data/ssd_mobilenet_v2.tflite
if [ ! -d test-data ]; then
  git clone https://github.com/GeoTIFF/test-data.git 
fi
for i in `seq 1 4`; do
  mkdir -p ../../docker/data/task${i}
done
cp sarcollector.py ../../docker/collectors
cp sarmapper.py ../../docker/mappers
i=3
rm -f test-data/files/abetow*.tiff
rm -f test-data/files/umbra*.tiff
for TIFF in `ls test-data/files/*.tiff`; do
  IDX=$(expr 1 + $i % 3)
  echo "$IDX $TIFF"
  cp ${TIFF} ../../docker/data/task${IDX}/
  i=`expr $i + 1`
done
echo "Submit example: python3 job.py -mi 1 -ma 4 -c 3 -ct sarcollector -mt sarmapper -r los -mr 1"
