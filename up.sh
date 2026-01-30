#! /bin/bash
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${DIR}
NAME=$1
./down.sh ${NAME}
docker compose -f compose${NAME}.yaml up --force-recreate --build -d
