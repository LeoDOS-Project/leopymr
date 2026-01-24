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

 
