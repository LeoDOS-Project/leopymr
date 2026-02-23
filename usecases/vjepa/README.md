# V-JEPA Use Case
This use case exemplifies how a Video-Joint Embedding Predictive Architecture (V-JEPA)
model can be used to process video frames in paralell and recognize various motions
based on pre-trained models from [Facebook FAIR](https://github.com/facebookresearch/vjepa2).
This example also demonstrate how to skip the map step and stream data directly
from collectors to the reducer.

## Sample Data
A small [sample video](https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4) 
or your own mp4 video (call it `sample.mp4` and place it in this directory before deploying).
may be used.

## Deployment
```
./deploy.sh
```

## Constellation Creation
```
MAX_SAT=7 MAX_ORB=7 SAT_RT=vjepa ./create_constellation.sh vjepa
```

## Job Execution
```
python3 job.py -mi 1 -ma 7 -c 10 -ct vjepacollector -r los -d docker/data/vjepa.json
```

## Results
The output of the job is a json dictionary with the detected labels and counts, e.g.:
```json
{
  "done": true,
  "jobid": "7c250207-2f2b-443b-90e4-61ce9c201aa8",
  "job_time": 106.12902903556824,
  "result": {
    "Showing [something] next to [something]": 17,
    "Showing [something] behind [something]": 23
  }
}
```
