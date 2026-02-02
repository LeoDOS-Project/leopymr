#! /bin/bash
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${DIR}
NAME=$1
docker compose -f compose${NAME}.yaml down --remove-orphans
