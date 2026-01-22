#! /bin/bash
./down.sh
docker compose up --force-recreate --build -d
