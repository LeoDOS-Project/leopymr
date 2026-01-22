#! /bin/bash
NAME=$1
docker compose -f compose${NAME}.yaml logs
