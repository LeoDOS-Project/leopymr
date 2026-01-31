# leopymr - SpaceCoMP implementation in Python
[![CoMP Test](https://github.com/LeoDOS-Project/leopymr/actions/workflows/test.yml/badge.svg)](https://github.com/LeoDOS-Project/leopymr/actions/workflows/test.yml)

## Getting Started
Create constellation testbed:
```
MAX_SAT=sats MAX_ORB=orbs ./create_constellation.sh myconstellation
```
where `sats` is the number of satellites in planes, `orbs` the number of planes
and `myconstellation` the name of the constellation.

Start up constellation:
```
./up.sh myconstellation
```

## Submit jobs
```
usage: job.py [-h] [-i ID] [-a {bipartite,random}] [-s SEED] [-r {los,center}] [-mi MINSAT] [-ma MAXSAT] [-c COLLECTORS] [-ct COLLECTTASK] [-mt MAPTASK]
              [-rt REDUCETASK] [-d DATA]

Submits and gets results from collect mapreduce task

options:
  -h, --help            show this help message and exit
  -i, --id ID           job id (specify to return results of job)
  -a, --allocator {bipartite,random}
                        map allocator
  -s, --seed SEED       random aoi shuffle seed
  -r, --reducetype {los,center}
                        reduce placement
  -mi, --minsat MINSAT  min aoi grid index
  -ma, --maxsat MAXSAT  max aoi grid index
  -c, --collectors COLLECTORS
                        total collectors (and mappers)
  -ct, --collecttask COLLECTTASK
                        collector task
  -mt, --maptask MAPTASK
                        mapper task
  -rt, --reducetask REDUCETASK
                        reducer task
  -d, --data DATA       job data file (json)
```

## Architecture
Each plane is represented by a separate
container in the same constellation docker network.
Each satellite is a process within the plane container.
A gateway REST reserver is exposed outside the constellation
to submit requests and obtain results.
The create constellation command above generates
a docker-compose script that can bring up and down the
testbed. All code is written in native python with minimal external dependencies.
 
## Paper
[Lightspeed Data Compute for the Space Era](https://arxiv.org/abs/2601.17589).
```
@misc{sandholm2026lightspeeddatacomputespace,
      title={Lightspeed Data Compute for the Space Era}, 
      author={Thomas Sandholm and Bernardo A. Huberman and Klas Segeljakt and Paris Carbone},
      year={2026},
      eprint={2601.17589},
      archivePrefix={arXiv},
      primaryClass={cs.DC},
      url={https://arxiv.org/abs/2601.17589}, 
}
```
