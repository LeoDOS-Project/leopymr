#! /bin/bash
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${DIR}
if [ ! -f sample.mp4 ]; then
  curl https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4 > sample.mp4
fi
if [ ! -d ../../docker/huggingface ]; then
  CLIOK=0
  which huggingface-cli && CLIOK=1
  if [ $CLIOK -eq 0 ]; then
    echo "Please install huggingface-cli" 
    exit 1
  fi
  huggingface-cli download facebook/vjepa2-vitl-fpc16-256-ssv2
  CACHEDIR=`huggingface-cli env | grep HF_HUB_CACHE | awk {'print $3'} | sed 's/\/hub$//'`
  if [ "X${CACHEDIR}" == "X" ]; then
    echo "Huggingface model download failed. Cache missing."
    exit 1
  fi
  cp -r ${CACHEDIR} ../../docker/
fi
cp sample.mp4 ../../docker/data/
cp vjepacollector.py ../../docker/collectors/
cp Dockerfile.vjepa ../../docker/
cp requirements.txt.vjepa ../../docker/

cat > vjepa.json <<ANY
{"filename":"data/sample.mp4"}
ANY
cp vjepa.json ../../docker/data/
echo "Constellation example: MAX_SAT=7 MAX_ORB=7 SAT_RT=vjepa ./create_constellation.sh vjepa"
echo "Submit example: python3 job.py -mi 1 -ma 7 -c 10 -ct vjepacollector -r los -d docker/data/vjepa.json"
