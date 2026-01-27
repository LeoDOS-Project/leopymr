# leopymr - SpaceCoMP implementation in Python

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
Example job submission script is in `submit.py`
and results can be collected with `completion.sh`
script.

## Submit jobs
```
usage: submit.py [-h] [-a {bipartite,random}] [-s SEED] [-r {los,center}] [-mi MINSAT]
                 [-ma MAXSAT] [-c COLLECTORS]

Submits collect mapreduce task

options:
  -h, --help            show this help message and exit
  -a, --allocator {bipartite,random}
                        map allocator
  -s, --seed SEED       random aoi shuffle seed
  -r, --reducetype {los,center}
                        reduce placement
  -mi, --minsat MINSAT  min aoi grid index
  -ma, --maxsat MAXSAT  max aoi grid index
  -c, --collectors COLLECTORS
                        total collectors (and mappers)```

## Architecture
Each plane is represented by a separate
container in the same constellation docker network.
Each satellite is a process within the plane container.
A gateway REST reserver is exposed outside the constellation
to submit requests and obtain results.
The create constellation command above generates
a docker-compose script that can bring up and down the
testbed. All code is written in native python
lwith minimal external dependencies.
 
