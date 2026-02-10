# SAR Use Case
This use case exemplifies how Synthetic Aperture Radar (SAR) images
can be processed with LeoCoMP. First denoising is done using
the [deepspeckling](https://github.com/hi-paris/deepdespeckling/tree/main) library,
in a custom collector. The denoised images are then streamed to
a custom mapper that performs object detection using the
[Google Mediapipe](https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector/) tool.
The top hits of objects detected are emitted to the standard reducer that just sums up the counts.

## Sample Data
We use noisy SAR data from [GeoTIFF](https://github.com/GeoTIFF/test-data.git) as input
and the `ssd_mobilenet_v2.tflite` model for detection. Note that the objects detected
are not accurate, which is not the point of this demo, but rather how both pre-=processing
and computer vision operation parameters can be easily parallelized, and data streamed.

## Deployment
```
./deploy.sh
```

## Constellation Creation
```
MAX_SAT=5 MAX_ORB=5 SAT_RT=sar ./create_constellation.sh sar
```

## Job Execution
```
python3 job.py -mi 1 -ma 4 -c 3 -ct sarcollector -mt sarmapper -r los -mr 1
```

## Results
The output of the job is a json dictionary of detected object counts.
