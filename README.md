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

## Submit Jobs
```
usage: job.py [-h] [-i ID] [-f FILE] [-a {bipartite,random}] [-s SEED] [-r {los,center}] [-mi MINSAT] [-ma MAXSAT] [-c COLLECTORS]
              [-ct COLLECTTASK] [-mt MAPTASK] [-rt REDUCETASK] [-d DATA] [-mr MAXRECORDS] [-u URL]

Submits and gets results from collect mapreduce task

options:
  -h, --help            show this help message and exit
  -i, --id ID           job id (specify to return results of job)
  -f, --file FILE       can be used with job id to download a job result file
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
  -mr, --maxrecords MAXRECORDS
                        max records to collect before streaming to mapper
  -u, --url URL         gateway server endpoint
```
## Job Completion Events
As an alternative to using the `-i` flag to poll for job results, a client
may also subscribe to an SSE event with the gateway.
```
python3 listen.py
```
All job completions will be pushed to all listeners
in the SSE format.
With `curl` this could also be achieved with:
```
curl -N "http://localhost:8089/subscribe"
```

## Native Clients
If the docker host does not run python or is missing any of
the python dependecies, bash scripts may be used as drop-in replacements for
`job.py` and `listen.py` called `job.sh` and `listen.sh` respectively.
The bash scripts only depend on `jq` and `curl`.

## Architecture
Each plane is represented by a separate
container in the same constellation docker network.
Each satellite is a process within the plane container.
A gateway REST server is exposed outside the constellation
to submit requests and obtain results.
The create constellation command above generates
a docker-compose script that can bring up and down the
testbed. All code is written in native python with minimal external dependencies.
All ISL communication is asynchronous, but the server executions
are synchronous. An example collector/mapper/reducer was implemented
to showcase a simple distributed wordcount job.
Custom tasks can be added into `docker/collectors`, `docker/mappers` and
`docker/reducers`.
 
## Paper
[Lightspeed Data Compute for the Space Era](https://arxiv.org/abs/2601.17589).
```bibtex
@article{sandholm2026lightspeed,
  title={Lightspeed Data Compute for the Space Era},
  author={Sandholm, Thomas and Huberman, Bernardo A and Segeljakt, Klas and Carbone, Paris},
  journal={arXiv preprint arXiv:2601.17589},
  year={2026}
}
```
