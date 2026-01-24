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
 
