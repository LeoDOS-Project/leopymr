# Docker Swarm Deployment
The easiest way to scale a constellation testbed beyond a single node is
with Docker swarm. Orbital planes are deployed in saprate containers
and can thus be put on different swarm nodes controlled by labels.

A local registry is deployed on the swarm intitiator node that are used
to publish the LeoCoMP gateway and orb images.

Simply create a constellation (a docker stack script will also be generated)
then run the `create_swarm.sh` script. The only requirements on the
non-initiator nodes is that they run `docker swarm join` and have access
to the registry node (and cun run the same images).

The containers are deployed in the exact same way as when all containers were
collocated, i.e. the gateway is expoosed to interact with the swarm. Which
means that the `job.py` script should work without any modifications
as long as it is run from the initiator node.

Note that to avoid exposing the registry externally it needs to be added
as an insecure-registries entry in the docker demon file, e.g. `/etc/docker/daemon.json`.
