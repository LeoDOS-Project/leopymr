#! /bin/bash
./down.sh
NAME=$1
docker compose -f compose${NAME}.yaml up --force-recreate --build -d
