# SpaceCoMP Visualization

This web based viasualization shows all message paths
between los, collectors, mappers and reducers from
a real run of a job based on logs replaid.

## Running a job
Follow the direction to create a constellation and run a job
[here](../README.md).

## Extract the logs
Run
```
./get_logs.sh myconstellation
```
where `myconstellation` is the name you gave to the
constellation when running the `create_constellation.sh`
script. This will create a log file called `myconstellation.jsonl`.

## Sart web server
Now start the web server with:
```
./start.sh
```
## Run web UI
The start script will print out a url with a port on the local host. Open that
URL in a web browser and select the `myconstellation.jsonl`
file to upload and start the simulation.
