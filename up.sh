#! /bin/bash
NAME=$1
./down.sh ${NAME}
docker compose -f compose${NAME}.yaml up --force-recreate --build -d
