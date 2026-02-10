# MISR Use Case
This use case exemplifies how Multi-Image(Frame) Super Resolution (MISR)
can be done with LeoCoMP. The collector simply converts a burts of images
in format `dng` to `png` and streams them to the mapper.
The mapper then uses the [Handheld Multi-Fram Super Resolution](https://sites.google.com/view/handheld-super-res/)
algorithm to combine images sent from the collector into a single image. The single
combined image is then sent to the reducer, which takes the images from all mappers
and combines them in the same way (with the same algorithm) to procude a final
output image.

## Sample Data
Sample burst images are taken from the [HDR+ dataset](https://hdrplusdata.org/dataset.html).

## Deployment
```
./deploy.sh
```

## Constellation Creation
```
MAX_SAT=5 MAX_ORB=5 SAT_RT=misr ./create_constellation.sh misr
```

## Job Execution
```
python3 job.py -mi 1 -ma 4 -c 3 -ct misrcollector -mt misrmapper -rt misrreducer -r los
```

## Results
The output of the job is a json dictionary with the name of the final combined image.
The image can be donwloaded with:
```
python3 job.py -i (job id) -f (file name)
```
